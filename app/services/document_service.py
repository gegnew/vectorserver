import logging
from uuid import UUID

from fastapi import Depends

from app.embeddings import Embedder
from app.exceptions import DatabaseError, DocumentNotFoundException, EmbeddingError
from app.models.chunk import Chunk
from app.models.document import Document
from app.repositories.chunk import ChunkRepository
from app.repositories.db import DB, get_db
from app.repositories.document import DocumentRepository

logger = logging.getLogger(__name__)


def get_document_service(db: DB = Depends(get_db)):
    return DocumentService(db)


class DocumentService:
    def __init__(self, db: DB):
        self.db = db
        self.embedder = Embedder()
        self.docs = DocumentRepository(self.db)
        self.chunks = ChunkRepository(self.db)

    async def create(self, document: Document) -> Document:
        try:
            # Use transaction to ensure document and chunks are created atomically
            async with self.db.transaction() as tx_db:
                created_doc = await self.docs.create_transactional(document, tx_db)
                if document.content:
                    chunks = self._chunk_and_embed_document(created_doc)
                    for chunk in chunks:
                        await self.chunks.create_transactional(chunk, tx_db)
            return created_doc
        except Exception as e:
            logger.error(f"Failed to create document {document.title}: {str(e)}")
            raise DatabaseError(f"Failed to create document: {str(e)}") from e

    async def get(self, document_id: UUID) -> Document:
        try:
            document = await self.docs.find(document_id)
            if not document:
                raise DocumentNotFoundException(document_id)
            return document
        except DocumentNotFoundException:
            raise
        except Exception as e:
            logger.error(f"Failed to get document {document_id}: {str(e)}")
            raise DatabaseError(f"Failed to get document: {str(e)}") from e

    async def update(
        self, document_id: UUID, title: str, content: str, metadata: dict = None
    ) -> Document:
        """Update a document and handle content changes."""
        if metadata is None:
            metadata = {}
        try:
            document = await self._get_and_validate_document(document_id)
            content_changed = self._is_content_changed(document.content, content)

            # Update document fields
            document.title = title
            document.content = content
            document.metadata = metadata
            updated_doc = await self.docs.update(document)

            if content_changed:
                await self._handle_content_change(document_id, updated_doc)

            return updated_doc
        except DocumentNotFoundException:
            raise
        except Exception as e:
            logger.error(f"Failed to update document {document_id}: {str(e)}")
            raise DatabaseError(f"Failed to update document: {str(e)}") from e

    async def _get_and_validate_document(self, document_id: UUID) -> Document:
        """Get document by ID and validate it exists."""
        document = await self.docs.find(document_id)
        if not document:
            raise DocumentNotFoundException(document_id)
        return document

    def _is_content_changed(self, old_content: str, new_content: str) -> bool:
        """Check if document content has changed."""
        return new_content != old_content

    async def _handle_content_change(
        self, document_id: UUID, document: Document
    ) -> None:
        """Handle content change by recreating chunks with new embeddings."""
        # Use transaction to ensure chunk operations are atomic
        async with self.db.transaction() as tx_db:
            await self._delete_existing_chunks(document_id, tx_db)

            if document.content:  # Only create chunks if content exists
                await self._create_new_chunks(document, tx_db)

        # Note: Caller should invalidate search indexes after this operation

    async def _delete_existing_chunks(self, document_id: UUID, tx_db) -> None:
        """Delete all existing chunks for a document."""
        old_chunks = await self.chunks.find_by_document(document_id)
        for chunk in old_chunks:
            await self.chunks.delete_transactional(chunk.id, tx_db)

    async def _create_new_chunks(self, document: Document, tx_db) -> None:
        """Create new chunks with embeddings for the document."""
        chunks = self._chunk_and_embed_document(document)
        for chunk in chunks:
            await self.chunks.create_transactional(chunk, tx_db)

    async def delete(self, document_id: UUID) -> bool:
        try:
            # First verify document exists
            await self.get(document_id)
            deleted_count = await self.docs.delete(document_id)
            return deleted_count > 0
        except DocumentNotFoundException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {str(e)}")
            raise DatabaseError(f"Failed to delete document: {str(e)}") from e

    def _chunk_and_embed_document(self, document: Document) -> list[Chunk]:
        try:
            (chunks, embeddings, chunk_lens, chunk_metadatas) = (
                self.embedder.chunk_and_embed(document.content)
            )

            chunk_objects = []
            for _j, (chunk, embedding, _chunk_len, chunk_metadata) in enumerate(
                zip(chunks, embeddings, chunk_lens, chunk_metadatas, strict=False)
            ):
                embedding_bytes = embedding.tobytes()

                # Merge chunking metadata with embedding metadata
                combined_metadata = {
                    **chunk_metadata,  # Smart chunker metadata
                    "embedding_model": self.embedder.model,
                    "embedding_dimension": len(embedding),
                    "dtype": str(embedding.dtype),
                    "document_title": document.title,
                    "document_id": str(document.id),
                }

                chunk_objects.append(
                    Chunk(
                        content=chunk,
                        document_id=document.id,
                        embedding=embedding_bytes,
                        metadata=combined_metadata,
                    )
                )
            return chunk_objects
        except Exception as e:
            logger.error(f"Failed to chunk and embed document {document.id}: {str(e)}")
            raise EmbeddingError(f"Failed to process document content: {str(e)}") from e
