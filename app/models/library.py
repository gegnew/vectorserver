"""Library models with proper inheritance and validation."""

from pydantic import BaseModel

from .base import BaseEntityModel


class LibraryBase(BaseModel):
    """Base library model with common fields."""

    name: str
    description: str | None = None


class Library(BaseEntityModel, LibraryBase):
    """Library with timestamps and metadata validation."""

    pass


class LibraryGet(LibraryBase):
    """Library model for GET responses."""

    pass


class LibraryCreate(LibraryBase):
    """Library model for creation requests."""

    pass


class LibraryUpdate(BaseModel):
    """Library model for update requests with optional fields."""

    name: str | None = None
    description: str | None = None
    metadata: dict | None = None
