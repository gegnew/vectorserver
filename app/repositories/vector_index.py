from abc import ABC, abstractmethod
from uuid import UUID
import numpy as np

from app.models.chunk import Chunk


class VectorIndexRepository(ABC):
    @abstractmethod
    def fit_chunks(self, chunks: list[Chunk]):
        raise NotImplementedError

    @abstractmethod
    def search_chunks(self, query_vector: np.ndarray, k: int = 5) -> list[Chunk]:
        raise NotImplementedError

    @abstractmethod
    def add_chunks(self, new_chunks: list[Chunk]):
        raise NotImplementedError

    @abstractmethod
    def remove_chunks(self, chunk_ids_to_remove: list[UUID]):
        raise NotImplementedError
