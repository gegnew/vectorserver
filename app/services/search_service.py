import logging
from typing import Literal
from uuid import UUID

from fastapi import Depends

from app.embeddings import Embedder
from app.exceptions import IndexError
from app.models.document import Document
from app.repositories.chunk import ChunkRepository
from app.repositories.db import DB, get_db
from app.repositories.document import DocumentRepository
from app.utils.persistent_index import PersistentFlatIndex, PersistentIVFIndex

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self, db: DB):
        self.db = db
        self.embedder = Embedder()
        self.chunks = ChunkRepository(self.db)
        self.docs = DocumentRepository(self.db)
        self.flat_index = PersistentFlatIndex()
        self.ivf_index = PersistentIVFIndex()
        self._loaded_indexes = {}

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
        similar_chunks = self._search_chunks(chunks, embedding, index_type, limit, library_id)
        
        # Get unique documents from similar chunks
        document_ids = list({chunk.document_id for chunk in similar_chunks})
        documents = []
        for doc_id in document_ids:
            doc = await self.docs.find(doc_id)
            if doc:
                documents.append(doc)
        
        return documents

    async def invalidate_index(self, library_id: UUID, index_type: str = None):
        """Invalidate cached indexes for a library."""
        if index_type:
            index_key = f"{library_id}_{index_type}"
            self._loaded_indexes.pop(index_key, None)
        else:
            # Invalidate all indexes for the library
            keys_to_remove = [k for k in self._loaded_indexes.keys() if k.startswith(str(library_id))]
            for key in keys_to_remove:
                self._loaded_indexes.pop(key, None)
        
        logger.info(f"Invalidated indexes for library {library_id}")

    async def delete_library_indexes(self, library_id: UUID):
        """Delete all persistent indexes for a library."""
        try:
            self.flat_index.delete_index(library_id)
            self.ivf_index.delete_index(library_id)
            await self.invalidate_index(library_id)
            logger.info(f"Deleted all indexes for library {library_id}")
        except Exception as e:
            logger.error(f"Failed to delete indexes for library {library_id}: {str(e)}")
            raise IndexError(f"Failed to delete indexes: {str(e)}") from e

    def _search_chunks(self, chunks, embedding, index_type: str, limit: int, library_id: UUID):
        """Search chunks using the specified index type with persistent indexes."""
        try:
            # Check if we need to load/update the index for this library
            index_key = f"{library_id}_{index_type}"
            
            match index_type:
                case "ivf":
                    if index_key not in self._loaded_indexes:
                        self.ivf_index.load_or_create_index(library_id, chunks)
                        self._loaded_indexes[index_key] = True
                    return self.ivf_index.search_chunks(embedding, k=limit)
                case "flat":
                    if index_key not in self._loaded_indexes:
                        self.flat_index.load_or_create_index(library_id, chunks)
                        self._loaded_indexes[index_key] = True
                    return self.flat_index.search_chunks(embedding, k=limit)
                case _:
                    raise ValueError(f"Unsupported index type: {index_type}")
        except Exception as e:
            logger.error(f"Search failed for library {library_id} with {index_type} index: {str(e)}")
            raise IndexError(f"Search operation failed: {str(e)}") from e


def get_search_service(db: DB = Depends(get_db)) -> SearchService:
    """Dependency to get SearchService instance."""
    return SearchService(db)