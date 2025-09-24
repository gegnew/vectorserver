"""Chunk models with proper inheritance and validation."""

from uuid import UUID

from pydantic import BaseModel

from .base import BaseEntityModel


class ChunkBase(BaseModel):
    """Base chunk model with common fields."""

    content: str
    embedding: bytes
    document_id: UUID


class Chunk(BaseEntityModel, ChunkBase):
    """Chunk with timestamps and metadata validation."""

    pass


class ChunkGet(ChunkBase):
    """Chunk model for GET responses."""
    
    # Include metadata for complete response
    metadata: dict | None = None


class ChunkCreate(ChunkBase):
    """Chunk model for creation requests."""
    
    # Include metadata field for creation
    metadata: dict | None = None


class ChunkUpdate(BaseModel):
    """Chunk model for update requests with optional fields."""

    content: str | None = None
    embedding: bytes | None = None
    metadata: dict | None = None
