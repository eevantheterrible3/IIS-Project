from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from repositories.document_section_repository import DocumentSectionRepository
from services.document_section_service import DocumentSectionService
from schemas.document_section_schema import DocumentSectionUpdateRequest, DocumentSectionResponse

router = APIRouter(prefix="/document-sections", tags=["Document Sections"])


@router.put("/{document_section_id}", response_model=DocumentSectionResponse)
async def update_document_section(
    document_section_id: int,
    request: DocumentSectionUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    service = DocumentSectionService(DocumentSectionRepository(db))
    return await service.update(document_section_id, request)
