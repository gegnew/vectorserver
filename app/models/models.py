from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class SearchText(BaseModel):
    content: str
    library_id: UUID
    index_type: Literal["ivf", "flat"] = "flat"
