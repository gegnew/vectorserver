from fastapi import APIRouter, status

from app.models.library import Library, LibraryCreate

router = APIRouter(prefix="/libraries", tags=["libraries"])


@router.post("", response_model=Library, status_code=status.HTTP_201_CREATED)
async def create_library(library_data: LibraryCreate):
    return {
        "name": "Test library",
        "description": "A test library",
    }
