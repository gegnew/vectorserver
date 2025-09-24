import numpy as np


class FlatIndex:
    def fit(self, vectors: np.ndarray) -> np.ndarray:
        """Fit the index with vectors and return transposed copy for efficient search."""
        return vectors.T.copy()  # return as (D, N) - features x samples

    def search(
        self, query_vector: np.ndarray, vectors: np.ndarray, k: int = 5
    ) -> list[int]:
        """Search for k most similar vectors and return index values."""
        if vectors is None or vectors.shape[1] == 0:
            return []

        similarities = self._cosine_similarity(query_vector, vectors)
        top_k_indices = np.argsort(similarities)[::-1][:k]
        return top_k_indices.tolist()

    def _cosine_similarity(self, query: np.ndarray, vectors: np.ndarray) -> np.ndarray:
        """Calculate cosine similarity between query and vectors."""
        similarities = np.squeeze(
            np.dot(query, vectors)
            / (np.linalg.norm(query) * np.linalg.norm(vectors, axis=0))
        )
        return similarities
