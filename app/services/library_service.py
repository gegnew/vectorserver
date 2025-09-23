import logging
from uuid import UUID

from fastapi import Depends

from app.exceptions import DatabaseError, LibraryNotFoundException
from app.models.document import Document
from app.models.library import Library
from app.repositories.db import DB, get_db
from app.repositories.document import DocumentRepository
from app.repositories.library import LibraryRepository

logger = logging.getLogger(__name__)


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
        try:
            return await self.libraries.create(library)
        except Exception as e:
            logger.error(f"Failed to create library {library.name}: {str(e)}")
            raise DatabaseError(f"Failed to create library: {str(e)}") from e


    async def get_library(self, library_id: UUID) -> Library:
        """Get a library by ID."""
        try:
            library = await self.libraries.find(library_id)
            if not library:
                raise LibraryNotFoundException(library_id)
            return library
        except LibraryNotFoundException:
            raise
        except Exception as e:
            logger.error(f"Failed to get library {library_id}: {str(e)}")
            raise DatabaseError(f"Failed to get library: {str(e)}") from e

    async def get_all_libraries(self) -> list[Library]:
        """Get all libraries."""
        try:
            libraries = await self.libraries.find_all()
            return list(libraries)
        except Exception as e:
            logger.error(f"Failed to get all libraries: {str(e)}")
            raise DatabaseError(f"Failed to get libraries: {str(e)}") from e

    async def get_library_documents(self, library_id: UUID) -> list[Document]:
        """Get all documents in a library."""
        try:
            # First verify library exists
            await self.get_library(library_id)
            documents = await self.docs.find_by_library(library_id)
            return list(documents)
        except LibraryNotFoundException:
            raise
        except Exception as e:
            logger.error(f"Failed to get documents for library {library_id}: {str(e)}")
            raise DatabaseError(f"Failed to get documents: {str(e)}") from e

    async def update_library(self, library: Library) -> Library:
        """Update an existing library."""
        try:
            updated_library = await self.libraries.update(library)
            if not updated_library:
                raise LibraryNotFoundException(library.id)
            return updated_library
        except KeyError:
            raise LibraryNotFoundException(library.id)
        except LibraryNotFoundException:
            raise
        except Exception as e:
            logger.error(f"Failed to update library {library.id}: {str(e)}")
            raise DatabaseError(f"Failed to update library: {str(e)}") from e

    async def delete_library(self, library_id: UUID) -> bool:
        """Delete a library by ID. Returns True if deleted successfully."""
        try:
            # First verify library exists
            await self.get_library(library_id)
            deleted_count = await self.libraries.delete(library_id)
            return deleted_count > 0
        except LibraryNotFoundException:
            raise
        except Exception as e:
            logger.error(f"Failed to delete library {library_id}: {str(e)}")
            raise DatabaseError(f"Failed to delete library: {str(e)}") from e

