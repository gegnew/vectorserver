from typing import Literal
from uuid import UUID

from app.embeddings import Embedder
from app.models.chunk import Chunk
from app.models.document import Document
from app.models.library import Library
from app.repositories.chunk import ChunkRepository
from app.repositories.db import get_db
from app.repositories.document import DocumentRepository
from app.repositories.library import LibraryRepository
from app.repositories.vector_index import FlatIndexRepository, IVFIndexRepository


def get_library_service():
    return LibraryService()


class LibraryService:
    def __init__(self):
        self.db = get_db()
        self.embedder = Embedder()
        self.libraries = LibraryRepository(self.db)
        self.docs = DocumentRepository(self.db)
        self.chunks = ChunkRepository(self.db)
        self.flat_index = FlatIndexRepository()
        self.ivf_index = IVFIndexRepository()

    def create(self, lib: Library) -> Library:
        return self.libraries.create(lib)

    def add_document(
        self, library_id: UUID, title: str, content: str, metadata: dict = None
    ):
        if metadata is None:
            metadata = {}
        doc = Document(
            title=title, content=content, metadata=metadata, library_id=library_id
        )
        self.docs.create(doc)
        chunks = self._chunk_and_embed_document(doc)
        return [self.chunks.create(chunk) for chunk in chunks]

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

    def get_library(self, id: UUID) -> Library:
        return self.libraries.find(id)

    def find_all(self) -> Library:
        return self.libraries.find_all()

    def get_docs(self, id: UUID) -> list[Document]:
        documents = self.docs.find_by_library(id)
        return documents

    def update(self, lib: Library):
        return self.libraries.update(lib)

    def delete(self, id: UUID):
        return self.libraries.delete(id)

    def search(
        self,
        search_str: str,
        id: UUID,
        index_type: Literal["flat", "ivf"] = "flat",
    ) -> Document | None:
        embedding = self.embedder.embed([search_str])[0]
        chunks = self.chunks.find_by_library(id)

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
            return self.docs.find(similar_chunks[0].document_id)
