from uuid import UUID

from fastapi import Depends

from app.models.document import Document
from app.models.library import Library
from app.repositories.db import DB, get_db
from app.repositories.document import DocumentRepository
from app.repositories.library import LibraryRepository


def get_library_service(db: DB = Depends(get_db)) -> LibraryService:
    """Dependency to get LibraryService instance."""
    return LibraryService(db)


class LibraryService:
    def __init__(self, db: DB):
        self.db = db
        self.libraries = LibraryRepository(self.db)
        self.docs = DocumentRepository(self.db)

    async def create_library(self, library: Library) -> Library:
        """Create a new library."""
        return await self.libraries.create(library)


    async def get_library(self, library_id: UUID) -> Library | None:
        """Get a library by ID."""
        return await self.libraries.find(library_id)

    async def get_all_libraries(self) -> list[Library]:
        """Get all libraries."""
        libraries = await self.libraries.find_all()
        return list(libraries)

    async def get_library_documents(self, library_id: UUID) -> list[Document]:
        """Get all documents in a library."""
        documents = await self.docs.find_by_library(library_id)
        return list(documents)

    async def update_library(self, library: Library) -> Library | None:
        """Update an existing library."""
        return await self.libraries.update(library)

    async def delete_library(self, library_id: UUID) -> int:
        """Delete a library by ID. Returns number of deleted rows."""
        return await self.libraries.delete(library_id)

