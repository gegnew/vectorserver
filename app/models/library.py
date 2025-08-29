from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class LibraryBase(BaseModel):
    name: str
    description: str
    documents: list[UUID]
    metadata: dict


class Library(LibraryBase):
    id: UUID = Field(default_factory=uuid4)


class LibraryGet(LibraryBase):
    pass


class LibraryCreate(LibraryBase):
    pass


class LibraryUpdate(LibraryBase):
    pass
