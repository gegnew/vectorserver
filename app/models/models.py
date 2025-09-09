from uuid import UUID

from pydantic import BaseModel


class SearchText(BaseModel):
    content: str
    library_id: UUID | None = None
