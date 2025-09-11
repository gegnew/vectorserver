from typing import Literal
from uuid import UUID

import numpy as np

from app.models.chunk import Chunk
from app.repositories.db import get_db
from app.repositories.vector_index import FlatIndexRepository
from app.utils.flat_index import FlatIndex
from app.utils.ivf import IVF


class VectorIndexService:
    def __init__(self, index_type: Literal["flat", "ivf"] = "flat", **kwargs):
        self.index_type = index_type
        self.db = get_db()

        match self.index_type:
            case "flat":
                self._repository = FlatIndexRepository()
            case "ivf":
                raise NotImplementedError
            case _:
                raise ValueError(f"Unknown index type: {index_type}")

    def fit(self, chunks: list[Chunk]):
        # TODO: load index from db
        # If no existing index or load failed, create new one
        self._repository.fit_chunks(chunks)

        # TODO: Save to db

    def search(self, query_vector: np.ndarray, k: int = 5) -> list[Chunk]:
        return self._repository.search_chunks(query_vector, k)

    def add_chunks(self, new_chunks: list[Chunk]):
        self._repository.add_chunks(new_chunks)

    def remove_chunks(self, chunk_ids: list[UUID]):
        self._repository.remove_chunks(chunk_ids)
