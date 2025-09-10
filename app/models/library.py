import json
from datetime import UTC, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class LibraryBase(BaseModel):
    name: str
    description: str | None = None
    metadata: dict | None = None

    @field_validator("metadata", mode="before")
    @classmethod
    def text_to_dict(cls, value: str | dict) -> str:
        match value:
            case str():
                return json.loads(value)
            case dict():
                return value


class Library(LibraryBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default=datetime.now(UTC))
    updated_at: datetime | None = None


class LibraryGet(LibraryBase):
    pass


class LibraryCreate(LibraryBase):
    pass


class LibraryUpdate(LibraryBase):
    pass
