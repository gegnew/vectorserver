from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.chunk import Chunk, ChunkUpdate
from app.services.chunk_service import ChunkService, get_chunk_service

router = APIRouter(prefix="/chunks", tags=["chunks"])


@router.get("", response_model=list[Chunk], status_code=status.HTTP_200_OK)
async def get_all_chunks(
    service: ChunkService = Depends(get_chunk_service),
):
    """Get all chunks."""
    return await service.get_all_chunks()


@router.get("/{chunk_id}", response_model=Chunk, status_code=status.HTTP_200_OK)
async def get_chunk(
    chunk_id: UUID,
    service: ChunkService = Depends(get_chunk_service),
):
    """Get a specific chunk by ID."""
    chunk = await service.get_chunk(chunk_id)
    if not chunk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Chunk {chunk_id} not found"
        )
    return chunk


@router.put("/{chunk_id}", response_model=Chunk, status_code=status.HTTP_200_OK)
async def update_chunk(
    chunk_id: UUID,
    chunk_update: ChunkUpdate,
    service: ChunkService = Depends(get_chunk_service),
):
    """Update an existing chunk."""
    updated_chunk = await service.update_chunk(chunk_id, chunk_update)
    if not updated_chunk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Chunk {chunk_id} not found"
        )
    return updated_chunk


@router.delete("/{chunk_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chunk(
    chunk_id: UUID,
    service: ChunkService = Depends(get_chunk_service),
):
    """Delete a chunk."""
    # First check if chunk exists
    existing_chunk = await service.get_chunk(chunk_id)
    if not existing_chunk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Chunk {chunk_id} not found"
        )

    deleted_count = await service.delete_chunk(chunk_id)
    if deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete chunk",
        )


@router.get(
    "/library/{library_id}", response_model=list[Chunk], status_code=status.HTTP_200_OK
)
async def get_chunks_by_library(
    library_id: UUID,
    service: ChunkService = Depends(get_chunk_service),
):
    """Get all chunks for a specific library."""
    return await service.get_chunks_by_library(library_id)
