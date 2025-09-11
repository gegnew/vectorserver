import numpy as np

from app.models.chunk import Chunk


class FlatIndex:
    def __init__(self):
        self.chunks = []
        self.vectors = None

    def fit(self, chunks: list[Chunk]):
        self.chunks = chunks
        if chunks:
            self.vectors = np.array(
                [np.frombuffer(chunk.embedding, dtype=np.float32) for chunk in chunks]
            ).T
        else:
            self.vectors = None

    def search(self, query_vector: np.ndarray, k: int = 5) -> list[Chunk]:
        """Search for k most similar chunks"""
        if not self.chunks or self.vectors is None:
            return []

        query = query_vector.reshape(1, -1)
        similarities = self._cosine_similarity(query, self.vectors)
        top_k_indices = np.argsort(similarities)[::-1][:k]

        return [self.chunks[i] for i in top_k_indices]

    def _cosine_similarity(self, query: np.ndarray, vectors: np.ndarray) -> np.ndarray:
        similarities = np.squeeze(
            np.dot(query, vectors)
            / (np.linalg.norm(query) * np.linalg.norm(vectors, axis=0))
        )
        return similarities
