from typing import Literal
from uuid import UUID

from fastapi import Depends

from app.embeddings import Embedder
from app.models.document import Document
from app.repositories.chunk import ChunkRepository
from app.repositories.db import DB, get_db
from app.repositories.document import DocumentRepository
from app.repositories.vector_index import FlatIndexRepository, IVFIndexRepository


class SearchService:
    def __init__(self, db: DB):
        self.db = db
        self.embedder = Embedder()
        self.chunks = ChunkRepository(self.db)
        self.docs = DocumentRepository(self.db)
        self.flat_index = FlatIndexRepository()
        self.ivf_index = IVFIndexRepository()

    async def search_similar_documents(
        self,
        search_text: str,
        library_id: UUID,
        index_type: Literal["flat", "ivf"] = "flat",
        limit: int = 1,
    ) -> list[Document]:
        """Search for similar documents in a library using vector similarity."""
        # Get embedding for search text
        embedding = self.embedder.embed([search_text])[0]
        
        # Get all chunks for the library
        chunks = await self.chunks.find_by_library(library_id)
        if not chunks:
            return []

        # Perform vector search based on index type
        similar_chunks = self._search_chunks(chunks, embedding, index_type, limit)
        
        # Get unique documents from similar chunks
        document_ids = list({chunk.document_id for chunk in similar_chunks})
        documents = []
        for doc_id in document_ids:
            doc = await self.docs.find(doc_id)
            if doc:
                documents.append(doc)
        
        return documents

    def _search_chunks(self, chunks, embedding, index_type: str, limit: int):
        """Search chunks using the specified index type."""
        match index_type:
            case "ivf":
                self.ivf_index.fit_chunks(chunks)
                return self.ivf_index.search_chunks(embedding, k=limit)
            case "flat":
                self.flat_index.fit_chunks(chunks)
                return self.flat_index.search_chunks(embedding, k=limit)
            case _:
                raise ValueError(f"Unsupported index type: {index_type}")


def get_search_service(db: DB = Depends(get_db)) -> SearchService:
    """Dependency to get SearchService instance."""
    return SearchService(db)