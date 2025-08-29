from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class ChunkBase(BaseModel):
    content: str
    embedding: str
    metadata: dict


class Chunk(ChunkBase):
    id: UUID = Field(default_factory=uuid4)


class ChunkGet(ChunkBase):
    pass


class ChunkCreate(ChunkBase):
    pass


class ChunkUpdate(ChunkBase):
    pass
