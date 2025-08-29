from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    name: str
    chunks: list[UUID]
    metadata: dict


class Document(DocumentBase):
    id: UUID = Field(default_factory=uuid4)


class DocumentGet(DocumentBase):
    pass


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(DocumentBase):
    pass
