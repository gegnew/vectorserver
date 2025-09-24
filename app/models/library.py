"""Library models with proper inheritance and validation."""

from pydantic import BaseModel, ConfigDict, Field

from .base import BaseEntityModel


class LibraryBase(BaseModel):
    """Base library model with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Library name")
    description: str | None = Field(
        None, max_length=1000, description="Optional library description"
    )


class Library(BaseEntityModel, LibraryBase):
    """Library with timestamps and metadata validation."""

    pass


class LibraryGet(LibraryBase):
    """Library model for GET responses."""

    pass


class LibraryCreate(LibraryBase):
    """Library model for creation requests."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Research Papers",
                    "description": "Collection of machine learning research papers",
                },
                {
                    "name": "Technical Documentation",
                    "description": "Internal API and system documentation",
                },
            ]
        }
    )


class LibraryUpdate(BaseModel):
    """Library model for update requests with optional fields."""

    name: str | None = None
    description: str | None = None
    metadata: dict | None = None
