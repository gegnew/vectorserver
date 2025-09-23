from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.library import Library, LibraryCreate, LibraryUpdate
from app.services.library_service import LibraryService, get_library_service

router = APIRouter(prefix="/libraries", tags=["libraries"])


@router.get("", response_model=list[Library], status_code=status.HTTP_200_OK)
async def get_libraries(
    service: LibraryService = Depends(get_library_service),
):
    return await service.get_all_libraries()


@router.get("/{library_id}", response_model=Library, status_code=status.HTTP_200_OK)
async def get_library(
    library_id: UUID,
    service: LibraryService = Depends(get_library_service),
):
    library = await service.get_library(library_id)
    if not library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Library {library_id} not found"
        )
    return library


@router.post("", response_model=Library, status_code=status.HTTP_201_CREATED)
async def create_library(
    library_data: LibraryCreate,
    service: LibraryService = Depends(get_library_service),
):
    try:
        lib = await service.create_library(Library(**library_data.model_dump()))
        return lib
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create library: {str(e)}"
        )


@router.put("/{library_id}", response_model=Library, status_code=status.HTTP_200_OK)
async def update_library(
    library_id: UUID,
    library_data: LibraryUpdate,
    service: LibraryService = Depends(get_library_service),
):
    # Ensure the library exists first
    existing_library = await service.get_library(library_id)
    if not existing_library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Library {library_id} not found"
        )
    
    # Update library with new data
    updated_library_data = library_data.model_dump(exclude_unset=True)
    updated_library_data["id"] = library_id
    updated_library = await service.update_library(Library(**updated_library_data))
    return updated_library


@router.delete("/{library_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_library(
    library_id: UUID,
    service: LibraryService = Depends(get_library_service),
):
    # Ensure the library exists first
    existing_library = await service.get_library(library_id)
    if not existing_library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Library {library_id} not found"
        )
    
    deleted = await service.delete_library(library_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete library"
        )


@router.get("/{library_id}/documents", response_model=list, status_code=status.HTTP_200_OK)
async def get_library_documents(
    library_id: UUID,
    service: LibraryService = Depends(get_library_service),
):
    """Get all documents in a library."""
    # Ensure the library exists first
    existing_library = await service.get_library(library_id)
    if not existing_library:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Library {library_id} not found"
        )
    
    documents = await service.get_library_documents(library_id)
    return documents
