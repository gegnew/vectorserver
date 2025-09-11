from abc import ABC, abstractmethod
from uuid import UUID
import numpy as np

from app.models.chunk import Chunk
from app.utils.flat_index import FlatIndex


class VectorIndexRepository(ABC):
    @abstractmethod
    def fit_chunks(self, chunks: list[Chunk]):
        raise NotImplementedError

    @abstractmethod
    def search_chunks(self, query_vector: np.ndarray, k: int = 5) -> list[Chunk]:
        raise NotImplementedError

    @abstractmethod
    def add_chunks(self, chunks: list[Chunk]):
        raise NotImplementedError

    @abstractmethod
    def remove_chunks(self, chunk_ids: list[UUID]):
        raise NotImplementedError


class FlatIndexRepository(VectorIndexRepository):
    def __init__(self, db=None):
        self.flat_index = FlatIndex()
        self._chunks = []
        self._vectors = None
        self._chunk_to_index_map = {}

    def fit_chunks(self, chunks: list[Chunk]):
        self._chunks = chunks
        if chunks:
            raw_vectors = self._chunks_to_vectors(chunks)
            self._vectors = self.flat_index.fit(raw_vectors)

    def search_chunks(self, query_vector: np.ndarray, k: int = 5) -> list[Chunk]:
        indices = self.flat_index.search(query_vector, self._vectors, k=k)
        return [self._chunks[i] for i in indices if i < len(self._chunks)]

    def _chunks_to_vectors(self, chunks: list[Chunk]) -> np.ndarray:
        return np.array(
            [np.frombuffer(chunk.embedding, dtype=np.float32) for chunk in chunks]
        )

    def add_chunks(self, chunks: list[Chunk]):
        start_index = len(self._chunks)
        self._chunks.extend(chunks)

        # Update mappings
        for i, chunk in enumerate(chunks):
            self._chunk_to_index_map[chunk.id] = start_index + i

        new_vectors = self._chunks_to_vectors(chunks)
        new_processed_vectors = self.flat_index.fit(new_vectors)
        if self._vectors is None:
            self._vectors = new_processed_vectors
        else:
            self._vectors = np.hstack([self._vectors, new_processed_vectors])

    def remove_chunks(self, chunk_ids: list[UUID]):
        pass
