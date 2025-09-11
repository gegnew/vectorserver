from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.models.library import Library, LibraryCreate, LibraryUpdate
from app.services.library_service import LibraryService, get_library_service

router = APIRouter(prefix="/libraries", tags=["libraries"])


@router.get("", response_model=list[Library], status_code=status.HTTP_200_OK)
async def get_libraries(
    service: LibraryService = Depends(get_library_service),
):
    return service.find_all()


@router.get("/{id}", response_model=Library, status_code=status.HTTP_200_OK)
async def get_library(
    id: UUID,
    service: LibraryService = Depends(get_library_service),
):
    return service.get_library(id)


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


@router.post("/{library_id}/documents", status_code=status.HTTP_201_CREATED)
async def add_document_to_library(
    library_id: UUID,
    document_data: dict,
    service: LibraryService = Depends(get_library_service),
):
    chunks = service.add_document(
        library_id=library_id,
        title=document_data["title"],
        content=document_data["content"],
        metadata=document_data.get("metadata", {}),
    )
    return {"chunks_created": len(chunks)}
