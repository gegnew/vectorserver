"""Smart text chunking with overlap and intelligent boundary detection."""

import re


class SmartChunker:
    """Advanced text chunker with overlap and boundary detection."""

    def __init__(
        self,
        chunk_size: int = 500,
        overlap_size: int = 50,
        min_chunk_size: int = 100,
        max_chunk_size: int = 1000,
    ):
        """Initialize the smart chunker with size and overlap parameters."""
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size

        # Patterns for detecting good boundary points (in order of preference)
        self.boundary_patterns = [
            r"\\n\\n+",  # Double newlines (paragraph breaks)
            r"\\n",  # Single newlines
            r"\\. ",  # End of sentences
            r"[.!?]\\s+",  # Sentence endings with punctuation
            r";\\s+",  # Semicolons
            r",\\s+",  # Commas
            r"\\s+",  # Any whitespace
        ]

    def chunk_text(self, text: str) -> list[tuple[str, dict]]:
        """Split text into overlapping chunks with intelligent boundary detection and return list of (chunk_text, metadata) tuples."""
        if not text or len(text) <= self.min_chunk_size:
            return [(text, self._create_chunk_metadata(0, len(text), 0, 1))]

        chunks = []
        start = 0
        chunk_number = 0

        while start < len(text):
            # Calculate the end position for this chunk
            target_end = start + self.chunk_size

            # If this would be the last chunk and it's too small, extend it
            remaining_text = len(text) - start
            if remaining_text <= self.chunk_size + self.min_chunk_size:
                chunk_text = text[start:]
                metadata = self._create_chunk_metadata(
                    start, len(text), chunk_number, None
                )
                chunks.append((chunk_text, metadata))
                break

            # Find the best boundary within our target range
            end = self._find_best_boundary(text, start, target_end)

            # Extract the chunk
            chunk_text = text[start:end]

            # Create metadata for this chunk
            metadata = self._create_chunk_metadata(
                start,
                end,
                chunk_number,
                None,  # Will set total chunks later
            )
            chunks.append((chunk_text, metadata))

            # Calculate the next start position with overlap
            next_start = max(start + 1, end - self.overlap_size)

            # Ensure we don't create overlapping chunks that are too similar
            if next_start >= end:
                next_start = end

            start = next_start
            chunk_number += 1

        # Update total chunks count in all metadata
        total_chunks = len(chunks)
        for i, (_, metadata) in enumerate(chunks):
            metadata["total_chunks"] = total_chunks
            metadata["is_first_chunk"] = i == 0
            metadata["is_last_chunk"] = i == total_chunks - 1

        return chunks

    def _find_best_boundary(self, text: str, start: int, target_end: int) -> int:
        """Find the best boundary point for splitting text."""
        # Don't go beyond the text length
        max_end = min(target_end + self.overlap_size, len(text))
        min_end = max(start + self.min_chunk_size, target_end - self.overlap_size)

        # If target_end is beyond text, return text length
        if target_end >= len(text):
            return len(text)

        # Look for good boundary points in order of preference
        for pattern in self.boundary_patterns:
            # Search for boundaries within the acceptable range
            search_text = text[min_end:max_end]
            matches = list(re.finditer(pattern, search_text))

            if matches:
                # Prefer boundaries closer to the target
                best_match = min(
                    matches, key=lambda m: abs((min_end + m.end()) - target_end)
                )
                return min_end + best_match.end()

        # If no good boundary found, just split at target
        return min(target_end, len(text))

    def _create_chunk_metadata(
        self, start: int, end: int, chunk_number: int, total_chunks: int
    ) -> dict:
        """Create metadata for a chunk."""
        return {
            "chunk_number": chunk_number,
            "total_chunks": total_chunks,
            "start_position": start,
            "end_position": end,
            "character_count": end - start,
            "has_overlap": chunk_number > 0,
            "overlap_size": self.overlap_size if chunk_number > 0 else 0,
            "chunking_method": "smart_boundary_detection",
            "chunk_size_target": self.chunk_size,
        }

    def get_chunk_overlap(
        self, chunks: list[tuple[str, dict]], chunk_index: int
    ) -> tuple[str, str]:
        """Get the overlapping text between a chunk and its neighbors and return (overlap_with_previous, overlap_with_next) tuple."""
        if chunk_index < 0 or chunk_index >= len(chunks):
            return "", ""

        overlap_prev = ""
        overlap_next = ""

        # Get overlap with previous chunk
        if chunk_index > 0:
            current_chunk = chunks[chunk_index][0]
            prev_chunk = chunks[chunk_index - 1][0]

            # Find common text at the beginning of current chunk
            # and end of previous chunk
            overlap_prev = self._find_text_overlap(
                prev_chunk, current_chunk, is_suffix=True
            )

        # Get overlap with next chunk
        if chunk_index < len(chunks) - 1:
            current_chunk = chunks[chunk_index][0]
            next_chunk = chunks[chunk_index + 1][0]

            # Find common text at the end of current chunk
            # and beginning of next chunk
            overlap_next = self._find_text_overlap(
                current_chunk, next_chunk, is_suffix=False
            )

        return overlap_prev, overlap_next

    def _find_text_overlap(self, text1: str, text2: str, is_suffix: bool) -> str:
        """Find overlapping text between two strings."""
        max_overlap = min(len(text1), len(text2), self.overlap_size * 2)

        for length in range(max_overlap, 0, -1):
            if is_suffix:
                # Check if end of text1 matches beginning of text2
                if text1[-length:] == text2[:length]:
                    return text1[-length:]
            else:
                # Check if end of text1 matches beginning of text2
                if text1[-length:] == text2[:length]:
                    return text1[-length:]

        return ""

    def merge_chunks(self, chunks: list[tuple[str, dict]]) -> str:
        """Merge chunks back into original text, handling overlaps."""
        if not chunks:
            return ""

        if len(chunks) == 1:
            return chunks[0][0]

        result = chunks[0][0]

        for i in range(1, len(chunks)):
            current_chunk = chunks[i][0]

            # Find and remove overlap
            overlap_prev, _ = self.get_chunk_overlap(chunks, i)

            if overlap_prev and current_chunk.startswith(overlap_prev):
                # Remove overlap from current chunk
                current_chunk = current_chunk[len(overlap_prev) :]

            result += current_chunk

        return result

    @classmethod
    def create_optimized_for_embeddings(cls) -> "SmartChunker":
        """Create a chunker optimized for embedding models."""
        return cls(
            chunk_size=512,  # Good size for most embedding models
            overlap_size=64,  # Reasonable overlap to preserve context
            min_chunk_size=128,  # Ensure chunks have enough content
            max_chunk_size=768,  # Stay within typical model limits
        )

    @classmethod
    def create_for_large_documents(cls) -> "SmartChunker":
        """Create a chunker optimized for large documents."""
        return cls(
            chunk_size=800,
            overlap_size=100,
            min_chunk_size=200,
            max_chunk_size=1200,
        )

    @classmethod
    def create_for_small_documents(cls) -> "SmartChunker":
        """Create a chunker optimized for smaller documents."""
        return cls(
            chunk_size=300,
            overlap_size=30,
            min_chunk_size=50,
            max_chunk_size=500,
        )
