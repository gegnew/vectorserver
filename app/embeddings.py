import cohere
import numpy as np

from .settings import settings
from .utils.smart_chunker import SmartChunker


class Embedder:
    def __init__(self):
        self.co = cohere.ClientV2(api_key=settings.cohere_api_key)
        self.model = "embed-v4.0"
        self.input_type = "search_query"
        self.chunker = SmartChunker.create_optimized_for_embeddings()

    def embed(self, phrases: list[str]):
        res = self.co.embed(
            texts=phrases,
            model=self.model,
            input_type=self.input_type,
            output_dimension=1024,
            embedding_types=["float"],
        )
        return np.array(res.embeddings.float)

    def _chunk_text(self, text: str):
        """Chunk text using smart chunking with overlap and boundary detection."""
        chunks_with_metadata = self.chunker.chunk_text(text)
        return [(chunk_text, metadata) for chunk_text, metadata in chunks_with_metadata]

    def chunk_and_embed(self, content: str):
        """
        Load, chunk, embed, and store in database with smart chunking.
        """
        chunks_with_metadata = self._chunk_text(content)

        if not chunks_with_metadata:
            return [], [], []

        # Extract chunks and their metadata
        chunks = [chunk_text for chunk_text, metadata in chunks_with_metadata]
        metadatas = [metadata for chunk_text, metadata in chunks_with_metadata]
        chunk_lens = [len(chunk) for chunk in chunks]

        # Get embeddings for all chunks
        embeddings = self.embed(chunks)

        return chunks, embeddings, chunk_lens, metadatas

    def cosine_similarity(self, query, vectors, k: int = 5):
        sims = np.squeeze(
            np.dot(query, vectors)
            / (np.linalg.norm(query) * (np.linalg.norm(vectors))).T
        )

        top_k_indices = np.argsort(sims)[::-1][:k]
        return sims[[top_k_indices]], top_k_indices
