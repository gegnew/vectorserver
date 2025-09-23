from datetime import UTC, datetime
from uuid import UUID

from fastapi import Depends

from app.models.chunk import Chunk, ChunkUpdate
from app.repositories.chunk import ChunkRepository
from app.repositories.db import get_database


class ChunkService:
    def __init__(self, chunk_repo: ChunkRepository):
        self.chunk_repo = chunk_repo

    async def get_chunk(self, chunk_id: UUID) -> Chunk | None:
        """Get a chunk by ID."""
        return await self.chunk_repo.find(chunk_id)

    async def get_all_chunks(self) -> list[Chunk]:
        """Get all chunks."""
        chunks = await self.chunk_repo.find_all()
        return list(chunks)

    async def get_chunks_by_library(self, library_id: UUID) -> list[Chunk]:
        """Get all chunks for a specific library."""
        return await self.chunk_repo.find_by_library(library_id)

    async def update_chunk(self, chunk_id: UUID, chunk_update: ChunkUpdate) -> Chunk | None:
        """Update an existing chunk."""
        # First get the existing chunk
        existing_chunk = await self.chunk_repo.find(chunk_id)
        if not existing_chunk:
            return None

        # Update only the fields that were provided
        update_data = chunk_update.model_dump(exclude_unset=True)
        
        # Create updated chunk with new values
        updated_chunk = existing_chunk.model_copy(update={
            **update_data,
            'updated_at': datetime.now(UTC)
        })

        return await self.chunk_repo.update(updated_chunk)

    async def delete_chunk(self, chunk_id: UUID) -> int:
        """Delete a chunk by ID. Returns number of deleted rows."""
        return await self.chunk_repo.delete(chunk_id)


def get_chunk_service(db=Depends(get_database)) -> ChunkService:
    """Dependency to get ChunkService instance."""
    chunk_repo = ChunkRepository(db)
    return ChunkService(chunk_repo)