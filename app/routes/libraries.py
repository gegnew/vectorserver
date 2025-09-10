from fastapi import APIRouter, Depends, status

from app.library_service import LibraryService, get_library_service
from app.models.library import Library, LibraryCreate

router = APIRouter(prefix="/libraries", tags=["libraries"])


@router.post("", response_model=Library, status_code=status.HTTP_201_CREATED)
async def create_library(
    library_data: LibraryCreate,
    service: LibraryService = Depends(get_library_service),
):
    lib = service.create(Library(**library_data.dict()))
    return lib
