"""Document models with proper inheritance and validation."""

from uuid import UUID

from pydantic import BaseModel, Field

from .base import BaseEntityModel


class DocumentBase(BaseModel):
    """Base document model with common fields."""

    title: str = Field(..., min_length=1, max_length=500, description="Document title")
    content: str | None = Field(None, max_length=50000, description="Document content")
    library_id: UUID = Field(..., description="ID of the parent library")


class Document(BaseEntityModel, DocumentBase):
    """Document with timestamps and metadata validation."""

    pass


class DocumentGet(DocumentBase):
    """Document model for GET responses."""
    
    # Include metadata and timestamps for complete response
    metadata: dict | None = None


class DocumentCreate(DocumentBase):
    """Document model for creation requests."""
    
    # Include metadata field for creation
    metadata: dict | None = None


class DocumentUpdate(BaseModel):
    """Document model for update requests with optional fields."""

    title: str | None = None
    content: str | None = None
    metadata: dict | None = None
