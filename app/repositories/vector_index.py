from abc import ABC, abstractmethod
from uuid import UUID

import numpy as np

from app.models.chunk import Chunk
from app.utils.flat_index import FlatIndex
from app.utils.ivf import IVF


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

    def _chunks_to_vectors(self, chunks: list[Chunk]) -> np.ndarray:
        return np.array([np.frombuffer(chunk.embedding) for chunk in chunks])


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
        chunk_ids_set = set(chunk_ids)

        indices_to_remove = [
            self._chunk_to_index_map[chunk_id]
            for chunk_id in chunk_ids
            if chunk_id in self._chunk_to_index_map
        ]
        self._chunks = [c for c in self._chunks if c.id not in chunk_ids_set]

        if self._vectors is not None and indices_to_remove:
            indices_to_remove = set(indices_to_remove)
            keep_mask = np.array(
                [i not in indices_to_remove for i in range(self._vectors.shape[1])]
            )
            self._vectors = self._vectors[:, keep_mask]

            if self._vectors.shape[1] == 0:
                self._vectors = None

        self._rebuild_index_map()

    def _rebuild_index_map(self):
        self._chunk_to_index_map = {chunk.id: i for i, chunk in enumerate(self._chunks)}


class IVFIndexRepository(VectorIndexRepository):
    def __init__(self, n_partitions: int = 16, max_iters: int = 32):
        self.n_partitions = n_partitions
        self.max_iters = max_iters
        self.ivf = IVF(n_clusters=n_partitions, max_iters=max_iters)
        self._chunks = []
        self.index_id = None

    def fit_chunks(self, chunks: list[Chunk]):
        self._chunks = chunks
        if chunks:
            vectors = self._chunks_to_vectors(chunks)
            self.ivf.fit(vectors)
            self.ivf.create_index(vectors)

    def search_chunks(self, query_vector: np.ndarray, k: int = 5) -> list[Chunk]:
        if not self._chunks:
            return []

        indices = self.ivf.search(query_vector)
        result_chunks = [self._chunks[i] for i in indices if i < len(self._chunks)]
        return result_chunks[:k]

    def add_chunks(self, chunks: list[Chunk]):
        self._chunks.extend(chunks)
        # for now, just rebuild index
        if self._chunks:
            vectors = self._chunks_to_vectors(self._chunks)
            self.ivf.fit(vectors)
            self.ivf.create_index(vectors)

    def remove_chunks(self, chunk_ids: list[UUID]):
        chunk_ids_set = set(chunk_ids)
        self._chunks = [c for c in self._chunks if c.id not in chunk_ids_set]
        if self._chunks:
            vectors = self._chunks_to_vectors(self._chunks)
            self.ivf.fit(vectors)
            self.ivf.create_index(vectors)
