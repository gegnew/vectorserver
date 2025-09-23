from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.exceptions import DatabaseError, DocumentNotFoundException, EmbeddingError
from app.models.document import Document, DocumentCreate
from app.services.document_service import DocumentService, get_document_service

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_document(
    document_data: DocumentCreate,
    service: DocumentService = Depends(get_document_service),
):
    try:
        document = Document(
            title=document_data.title,
            content=document_data.content or "",
            library_id=document_data.library_id,
            metadata=document_data.metadata or {},
        )
        created_doc = await service.create(document)
        return {"message": "Document created successfully", "id": str(created_doc.id)}
    except EmbeddingError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{document_id}", response_model=Document, status_code=status.HTTP_200_OK)
async def get_document(
    document_id: UUID,
    service: DocumentService = Depends(get_document_service),
):
    try:
        return await service.get(document_id)
    except DocumentNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{document_id}", response_model=Document, status_code=status.HTTP_200_OK)
async def update_document(
    document_id: UUID,
    document_data: DocumentCreate,
    service: DocumentService = Depends(get_document_service),
):
    try:
        updated_doc = await service.update(
            document_id=document_id,
            title=document_data.title,
            content=document_data.content or "",
            metadata=document_data.metadata or {},
        )
        return updated_doc
    except DocumentNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except EmbeddingError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    service: DocumentService = Depends(get_document_service),
):
    try:
        await service.delete(document_id)
    except DocumentNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
