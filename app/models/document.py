"""Document models with proper inheritance and validation."""

from uuid import UUID

from pydantic import BaseModel

from .base import BaseEntityModel


class DocumentBase(BaseModel):
    """Base document model with common fields."""

    title: str
    content: str | None = None
    library_id: UUID


class Document(BaseEntityModel, DocumentBase):
    """Document with timestamps and metadata validation."""

    pass


class DocumentGet(DocumentBase):
    """Document model for GET responses."""

    pass


class DocumentCreate(DocumentBase):
    """Document model for creation requests."""

    pass


class DocumentUpdate(BaseModel):
    """Document model for update requests with optional fields."""

    title: str | None = None
    content: str | None = None
    metadata: dict | None = None
