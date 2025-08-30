from pydantic import BaseModel


class SearchText(BaseModel):
    content: str
