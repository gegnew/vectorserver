import json
from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class ChunkBase(BaseModel):
    content: str
    embedding: bytes
    metadata: dict | None = None
    document_id: UUID

    @field_validator("metadata", mode="before")
    @classmethod
    def text_to_dict(cls, value: str | dict | None) -> dict | None:
        if isinstance(value, str):
            return json.loads(value)
        return value


class Chunk(ChunkBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default=datetime.now(UTC))
    updated_at: datetime | None = None


class ChunkGet(ChunkBase):
    pass


class ChunkCreate(ChunkBase):
    pass


class ChunkUpdate(BaseModel):
    content: str | None = None
    embedding: bytes | None = None
    metadata: dict | None = None
