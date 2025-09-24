from fastapi import APIRouter, Depends, HTTPException, status

from app.exceptions import ValidationError
from app.models.models import SearchResult, SearchText
from app.services.search_service import SearchService, get_search_service

router = APIRouter(prefix="/search", tags=["search"])


@router.post("", response_model=list[SearchResult], status_code=status.HTTP_200_OK)
async def search_similar(
    search_data: SearchText, service: SearchService = Depends(get_search_service)
):
    """Search for similar documents in a library with optional metadata filtering."""
    try:
        search_results = await service.search_similar_documents(
            search_text=search_data.content,
            library_id=search_data.library_id,
            index_type=search_data.index_type,
            limit=search_data.limit,
            metadata_filters=search_data.metadata_filters,
        )

        return search_results or []
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        ) from e
