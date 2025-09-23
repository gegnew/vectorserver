from fastapi import APIRouter, Depends, HTTPException, status

from app.models.document import Document
from app.models.models import SearchText
from app.services.search_service import SearchService, get_search_service

router = APIRouter(prefix="/search", tags=["search"])


@router.post("", response_model=list[Document], status_code=status.HTTP_200_OK)
async def search_similar(
    search_data: SearchText, service: SearchService = Depends(get_search_service)
):
    """Search for similar documents in a library."""
    documents = await service.search_similar_documents(
        search_text=search_data.content,
        library_id=search_data.library_id,
        index_type=search_data.index_type,
        limit=5  # Return top 5 similar documents
    )

    if not documents:
        raise HTTPException(
            status_code=404,
            detail="No matching documents found for the search query"
        )

    return documents
