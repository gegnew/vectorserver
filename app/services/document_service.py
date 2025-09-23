from uuid import UUID

from fastapi import Depends

from app.embeddings import Embedder
from app.models.chunk import Chunk
from app.models.document import Document
from app.repositories.chunk import ChunkRepository
from app.repositories.db import DB, get_db
from app.repositories.document import DocumentRepository


def get_document_service(db: DB = Depends(get_db)):
    return DocumentService(db)


class DocumentService:
    def __init__(self, db: DB):
        self.db = db
        self.embedder = Embedder()
        self.docs = DocumentRepository(self.db)
        self.chunks = ChunkRepository(self.db)

    async def create(self, document: Document) -> Document:
        created_doc = await self.docs.create(document)
        if document.content:
            chunks = self._chunk_and_embed_document(created_doc)
            for chunk in chunks:
                await self.chunks.create(chunk)
        return created_doc

    async def get(self, document_id: UUID) -> Document:
        return await self.docs.find(document_id)

    async def update(
        self, document_id: UUID, title: str, content: str, metadata: dict = None
    ) -> Document:
        if metadata is None:
            metadata = {}
        doc = await self.docs.find(document_id)
        if doc:
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
        return None

    async def delete(self, document_id: UUID) -> int:
        return await self.docs.delete(document_id)

    def _chunk_and_embed_document(self, document: Document) -> list[Chunk]:
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
