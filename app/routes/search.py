from fastapi import APIRouter, Depends, status

from app.models.document import Document
from app.models.models import SearchText
from app.services.library_service import LibraryService, get_library_service

router = APIRouter(prefix="/search", tags=["search"])


@router.post("", response_model=Document, status_code=status.HTTP_200_OK)
async def search_similar(
    search_data: SearchText, service: LibraryService = Depends(get_library_service)
):
    doc = service.search(
        search_str=search_data.content,
        id=search_data.library_id,
        index_type=search_data.index_type,
    )
    return doc
