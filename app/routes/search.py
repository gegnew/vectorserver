from fastapi import APIRouter, Depends

from app.db import get_db
from app.models.models import SearchText

router = APIRouter(prefix="/search", tags=["search"])


# @router.post("", response_model=Document, status_code=status.HTTP_200_OK)
@router.post("")
async def search_similar(search_data: SearchText, db=Depends(get_db)):
    doc = db.search_similar(content=search_data.content)
    return doc
