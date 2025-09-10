from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.library_service import LibraryService, get_library_service
from app.models.library import Library, LibraryCreate, LibraryUpdate

router = APIRouter(prefix="/libraries", tags=["libraries"])


@router.post("", response_model=Library, status_code=status.HTTP_201_CREATED)
async def create_library(
    library_data: LibraryCreate,
    service: LibraryService = Depends(get_library_service),
):
    lib = service.create(Library(**library_data.dict()))
    return lib


@router.put("", response_model=Library, status_code=status.HTTP_201_CREATED)
async def update_library(
    library_data: LibraryUpdate,
    service: LibraryService = Depends(get_library_service),
):
    return service.update(Library(**library_data.dict()))


@router.delete("", status_code=status.HTTP_202_ACCEPTED)
async def delete_library(
    id: UUID,
    service: LibraryService = Depends(get_library_service),
):
    deleted = service.delete(id)
    return {"deleted": deleted}
