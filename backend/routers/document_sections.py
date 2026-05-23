from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from database import get_db
from models.user import User
from repositories.document_section_repository import DocumentSectionRepository
from schemas.document_section_schema import DocumentSectionResponse, DocumentSectionUpdateRequest
from services.document_section_service import DocumentSectionService

router = APIRouter(prefix="/document-sections", tags=["Document Sections"])


@router.put("/{document_section_id}", response_model=DocumentSectionResponse)
async def update_document_section(
    document_section_id: int,
    request: DocumentSectionUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DocumentSectionService(DocumentSectionRepository(db))
    return await service.update(document_section_id, request)
