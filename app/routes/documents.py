from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.document import Document, DocumentCreate
from app.services.document_service import DocumentService, get_document_service

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_document(
    document_data: DocumentCreate,
    service: DocumentService = Depends(get_document_service),
):
    document = Document(
        title=document_data.title,
        content=document_data.content or "",
        library_id=document_data.library_id,
        metadata=document_data.metadata or {},
    )
    created_doc = await service.create(document)
    return {"message": "Document created successfully", "id": str(created_doc.id)}


@router.get("/{document_id}", response_model=Document, status_code=status.HTTP_200_OK)
async def get_document(
    document_id: UUID,
    service: DocumentService = Depends(get_document_service),
):
    document = await service.get(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )
    return document


@router.put("/{document_id}", response_model=Document, status_code=status.HTTP_200_OK)
async def update_document(
    document_id: UUID,
    document_data: DocumentCreate,
    service: DocumentService = Depends(get_document_service),
):
    updated_doc = await service.update(
        document_id=document_id,
        title=document_data.title,
        content=document_data.content or "",
        metadata=document_data.metadata or {},
    )
    if not updated_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )
    return updated_doc


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    service: DocumentService = Depends(get_document_service),
):
    deleted = await service.delete(document_id)
    if deleted == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )
