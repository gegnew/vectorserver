"""Custom exception classes for the Vector Database API."""

from uuid import UUID


class VectorDBException(Exception):
    """Base exception for all Vector DB related errors."""

    pass


class ResourceNotFoundException(VectorDBException):
    """Raised when a requested resource is not found."""

    def __init__(self, resource_type: str, resource_id: UUID | str):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(f"{resource_type} {resource_id} not found")


class LibraryNotFoundException(ResourceNotFoundException):
    """Raised when a library is not found."""

    def __init__(self, library_id: UUID):
        super().__init__("Library", library_id)


class DocumentNotFoundException(ResourceNotFoundException):
    """Raised when a document is not found."""

    def __init__(self, document_id: UUID):
        super().__init__("Document", document_id)


class ChunkNotFoundException(ResourceNotFoundException):
    """Raised when a chunk is not found."""

    def __init__(self, chunk_id: UUID):
        super().__init__("Chunk", chunk_id)


class ValidationError(VectorDBException):
    """Raised when data validation fails."""

    pass


class DatabaseError(VectorDBException):
    """Raised when database operations fail."""

    pass


class EmbeddingError(VectorDBException):
    """Raised when embedding operations fail."""

    pass


class IndexError(VectorDBException):
    """Raised when vector index operations fail."""

    pass
