import numpy as np

from app.models.chunk import Chunk


class FlatIndex:
    def __init__(self):
        self.chunks = []
        self.vectors = None

    def fit(self, vectors: np.ndarray):
        """Fit the index with vectors (N, D) where N=samples, D=dimensions"""
        self.vectors = vectors.T.copy()  # Store as (D, N) - features × samples

    def search(self, query_vector: np.ndarray, k: int = 5) -> list[int]:
        """Search for k most similar vectors

        Return: index values
        """
        if self.vectors is None or len(self.vectors) == 0:
            return []

        similarities = self._cosine_similarity(query_vector, self.vectors)
        top_k_indices = np.argsort(similarities)[::-1][:k]

        return top_k_indices.tolist()

    def _cosine_similarity(self, query: np.ndarray, vectors: np.ndarray) -> np.ndarray:
        similarities = np.squeeze(
            np.dot(query, vectors)
            / (np.linalg.norm(query) * np.linalg.norm(vectors, axis=0))
        )
        return similarities
