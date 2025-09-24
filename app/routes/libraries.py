from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.exceptions import DatabaseError, LibraryNotFoundException
from app.models.library import Library, LibraryCreate, LibraryUpdate
from app.services.library_service import LibraryService, get_library_service

router = APIRouter(prefix="/libraries", tags=["libraries"])


@router.get("", response_model=list[Library], status_code=status.HTTP_200_OK)
async def get_libraries(
    service: LibraryService = Depends(get_library_service),
):
    """Get all libraries."""
    return await service.get_all_libraries()


@router.get("/{library_id}", response_model=Library, status_code=status.HTTP_200_OK)
async def get_library(
    library_id: UUID,
    service: LibraryService = Depends(get_library_service),
):
    try:
        return await service.get_library(library_id)
    except LibraryNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@router.post("", response_model=Library, status_code=status.HTTP_201_CREATED)
async def create_library(
    library_data: LibraryCreate,
    service: LibraryService = Depends(get_library_service),
):
    try:
        lib = await service.create_library(Library(**library_data.model_dump()))
        return lib
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@router.put("/{library_id}", response_model=Library, status_code=status.HTTP_200_OK)
async def update_library_by_path(
    library_id: UUID,
    library_data: LibraryUpdate,
    service: LibraryService = Depends(get_library_service),
):
    try:
        # Get existing library to merge with update data
        existing_library = await service.get_library(library_id)

        # Update library with new data
        updated_library_data = existing_library.model_dump()
        updated_library_data.update(library_data.model_dump(exclude_unset=True))
        updated_library_data["id"] = library_id

        updated_library = await service.update_library(Library(**updated_library_data))
        return updated_library
    except LibraryNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@router.put("", response_model=Library, status_code=status.HTTP_200_OK)
async def update_library(
    library_data: Library,
    service: LibraryService = Depends(get_library_service),
):
    try:
        updated_library = await service.update_library(library_data)
        return updated_library
    except LibraryNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@router.delete("/{library_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_library_by_path(
    library_id: UUID,
    service: LibraryService = Depends(get_library_service),
):
    try:
        await service.delete_library(library_id)
    except LibraryNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


# Note: Removed duplicate DELETE endpoint with query param - use /{library_id} instead


@router.get(
    "/{library_id}/documents", response_model=list, status_code=status.HTTP_200_OK
)
async def get_library_documents(
    library_id: UUID,
    service: LibraryService = Depends(get_library_service),
):
    """Get all documents in a library."""
    try:
        documents = await service.get_library_documents(library_id)
        return documents
    except LibraryNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e
