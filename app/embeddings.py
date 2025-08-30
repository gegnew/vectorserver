import cohere
import numpy as np

from .settings import settings


class Embedder:
    def __init__(self):
        self.co = cohere.ClientV2(api_key=settings.cohere_api_key)
        self.model = "embed-v4.0"
        self.input_type = "search_query"

    def embed(self, phrases: list[str]):
        res = self.co.embed(
            texts=phrases,
            model=self.model,
            input_type=self.input_type,
            output_dimension=1024,
            embedding_types=["float"],
        )
        return np.array(res.embeddings.float)

    def _chunk_text(self, text: str, chunk_size: int = 500):
        start = 0
        end = 0
        while start + chunk_size < len(text) and end != -1:
            end = text.rfind(" ", start, start + chunk_size + 1)
            yield text[start:end]
            start = end + 1
        yield text[start:]

    def chunk_and_embed(self, content: str):
        """
        Load, chunk, embed, and store in database.
        """
        chunks_gen = self._chunk_text(content)
        chunks = [(n, len(n)) for n in chunks_gen]

        chunks, chunk_lens = zip(*chunks)
        embeddings = self.embed(chunks)
        return chunks, embeddings, chunk_lens

    def cosine_similarity(self, query, vectors, k: int = 5):
        """cosine_sim = (A · B) / (||A|| * ||B||)"""

        vectors = vectors.T
        dot_product = np.dot(query, vectors)
        magnitude_A = np.linalg.norm(query)
        magnitude_B = np.linalg.norm(vectors)

        sims = dot_product / (magnitude_A * magnitude_B)

        top_k_indices = np.argsort(sims)[::-1][:k]
        return sims[[top_k_indices]], top_k_indices
