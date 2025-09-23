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
            created_doc = await self.docs.create(document)
            if document.content:
                chunks = self._chunk_and_embed_document(created_doc)
                for chunk in chunks:
                    await self.chunks.create(chunk)
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
        if metadata is None:
            metadata = {}
        try:
            doc = await self.docs.find(document_id)
            if not doc:
                raise DocumentNotFoundException(document_id)
                
            # Check if content is being changed
            content_changed = content != doc.content
            
            # Update document fields
            doc.title = title
            doc.content = content
            doc.metadata = metadata
            updated_doc = await self.docs.update(doc)

            # re-chunk and re-embed if content changed
            if content_changed:
                # Delete old chunks
                old_chunks = await self.chunks.find_by_document(document_id)
                for chunk in old_chunks:
                    await self.chunks.delete(chunk.id)

                # create new chunks
                if content:
                    chunks = self._chunk_and_embed_document(updated_doc)
                    for chunk in chunks:
                        await self.chunks.create(chunk)

            return updated_doc
        except DocumentNotFoundException:
            raise
        except Exception as e:
            logger.error(f"Failed to update document {document_id}: {str(e)}")
            raise DatabaseError(f"Failed to update document: {str(e)}") from e

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
            chunks, embeddings, chunk_lens = self.embedder.chunk_and_embed(document.content)

            chunk_objects = []
            for j, (chunk, embedding, chunk_len) in enumerate(
                zip(chunks, embeddings, chunk_lens, strict=False)
            ):
                embedding_bytes = embedding.tobytes()

                chunk_objects.append(
                    Chunk(
                        content=chunk,
                        document_id=document.id,
                        embedding=embedding_bytes,
                        metadata={
                            "chunk_number": j,
                            "total_chunks": len(chunks),
                            "character_count": chunk_len,
                            "embedding_model": self.embedder.model,
                            "embedding_dimension": len(embedding),
                            "dtype": str(embedding.dtype),
                        },
                    )
                )
            return chunk_objects
        except Exception as e:
            logger.error(f"Failed to chunk and embed document {document.id}: {str(e)}")
            raise EmbeddingError(f"Failed to process document content: {str(e)}") from e
