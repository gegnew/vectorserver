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
    
    # Include metadata for complete response
    metadata: dict | None = None


class LibraryCreate(LibraryBase):
    """Library model for creation requests."""
    
    # Include metadata field for creation
    metadata: dict | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Research Papers",
                    "description": "Collection of machine learning research papers",
                    "metadata": {"source": "arxiv", "category": "ML"}
                },
                {
                    "name": "Technical Documentation", 
                    "description": "Internal API and system documentation",
                    "metadata": {"type": "internal", "team": "engineering"}
                },
            ]
        }
    )


class LibraryUpdate(BaseModel):
    """Library model for update requests with optional fields."""

    name: str | None = None
    description: str | None = None
    metadata: dict | None = None
