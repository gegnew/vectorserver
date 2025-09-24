from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.exceptions import IndexError as VectorIndexError
from app.services.search_service import SearchService, get_search_service

router = APIRouter(prefix="/indexes", tags=["indexes"])


@router.delete("/libraries/{library_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_library_indexes(
    library_id: UUID,
    service: SearchService = Depends(get_search_service),
):
    """Delete all indexes for a specific library."""
    try:
        await service.delete_library_indexes(library_id)
    except VectorIndexError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@router.post(
    "/libraries/{library_id}/invalidate", status_code=status.HTTP_204_NO_CONTENT
)
async def invalidate_library_indexes(
    library_id: UUID,
    service: SearchService = Depends(get_search_service),
):
    """Invalidate cached indexes for a library to force rebuild on next search."""
    try:
        await service.invalidate_index(library_id)
    except VectorIndexError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@router.get("/health", status_code=status.HTTP_200_OK)
async def index_health_check():
    """Check if index storage is accessible."""
    try:
        from pathlib import Path

        storage_path = Path("data/indexes")
        storage_path.mkdir(parents=True, exist_ok=True)
        return {"status": "healthy", "storage_path": str(storage_path.absolute())}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Index storage not accessible: {str(e)}",
        ) from e
