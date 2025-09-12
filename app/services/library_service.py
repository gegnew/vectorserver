from typing import Literal
from uuid import UUID

from fastapi import Depends

from app.embeddings import Embedder
from app.models.chunk import Chunk
from app.models.document import Document
from app.models.library import Library
from app.repositories.chunk import ChunkRepository
from app.repositories.db import DB, get_db
from app.repositories.document import DocumentRepository
from app.repositories.library import LibraryRepository
from app.repositories.vector_index import FlatIndexRepository, IVFIndexRepository


def get_library_service(db: DB = Depends(get_db)):
    return LibraryService(db)


class LibraryService:
    def __init__(self, db: DB):
        self.db = db
        self.embedder = Embedder()
        self.libraries = LibraryRepository(self.db)
        self.docs = DocumentRepository(self.db)
        self.chunks = ChunkRepository(self.db)
        self.flat_index = FlatIndexRepository()
        self.ivf_index = IVFIndexRepository()

    async def create(self, lib: Library) -> Library:
        return await self.libraries.create(lib)

    async def add_document(
        self, library_id: UUID, title: str, content: str, metadata: dict = None
    ):
        if metadata is None:
            metadata = {}
        doc = Document(
            title=title, content=content, metadata=metadata, library_id=library_id
        )
        await self.docs.create(doc)
        chunks = self._chunk_and_embed_document(doc)
        created_chunks = []
        for chunk in chunks:
            created_chunk = await self.chunks.create(chunk)
            created_chunks.append(created_chunk)
        return created_chunks

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

    async def get_library(self, id: UUID) -> Library:
        return await self.libraries.find(id)

    async def find_all(self) -> Library:
        return await self.libraries.find_all()

    async def get_docs(self, id: UUID) -> list[Document]:
        documents = await self.docs.find_by_library(id)
        return documents

    async def update(self, lib: Library):
        return await self.libraries.update(lib)

    async def delete(self, id: UUID):
        return await self.libraries.delete(id)

    async def search(
        self,
        search_str: str,
        id: UUID,
        index_type: Literal["flat", "ivf"] = "flat",
    ) -> Document | None:
        embedding = self.embedder.embed([search_str])[0]
        chunks = await self.chunks.find_by_library(id)

        if not chunks:
            return None

        match index_type:
            case "ivf":
                self.ivf_index.fit_chunks(chunks)
                similar_chunks = self.ivf_index.search_chunks(embedding, k=1)
            case "flat":
                self.flat_index.fit_chunks(chunks)
                similar_chunks = self.flat_index.search_chunks(embedding, k=1)

        if similar_chunks:
            return await self.docs.find(similar_chunks[0].document_id)
