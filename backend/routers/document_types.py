from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from repositories.document_type_repository import DocumentTypeRepository
from repositories.section_template_repository import SectionTemplateRepository
from services.document_type_service import DocumentTypeService
from services.section_template_service import SectionTemplateService
from schemas.document_type_schema import (
    DocumentTypeCreateRequest,
    DocumentTypeUpdateRequest,
    DocumentTypeResponse,
    DocumentTypeDetailResponse,
)
from schemas.section_template_schema import (
    SectionTemplateCreateRequest,
    SectionTemplateUpdateRequest,
    SectionTemplateResponse,
)

router = APIRouter(prefix="/document-types", tags=["Document Types"])


@router.get("", response_model=List[DocumentTypeResponse])
async def get_all_document_types(db: AsyncSession = Depends(get_db)):
    service = DocumentTypeService(DocumentTypeRepository(db))
    return await service.get_all()


@router.get("/{document_type_id}", response_model=DocumentTypeDetailResponse)
async def get_document_type(document_type_id: int, db: AsyncSession = Depends(get_db)):
    service = DocumentTypeService(DocumentTypeRepository(db))
    return await service.get_by_id(document_type_id)


@router.post("", response_model=DocumentTypeResponse)
async def create_document_type(
    request: DocumentTypeCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    service = DocumentTypeService(DocumentTypeRepository(db))
    return await service.create(request)


@router.put("/{document_type_id}", response_model=DocumentTypeResponse)
async def update_document_type(
    document_type_id: int,
    request: DocumentTypeUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    service = DocumentTypeService(DocumentTypeRepository(db))
    return await service.update(document_type_id, request)


@router.delete("/{document_type_id}")
async def delete_document_type(document_type_id: int, db: AsyncSession = Depends(get_db)):
    service = DocumentTypeService(DocumentTypeRepository(db))
    return await service.delete(document_type_id)


@router.get("/{document_type_id}/section-templates", response_model=List[SectionTemplateResponse])
async def get_section_templates(document_type_id: int, db: AsyncSession = Depends(get_db)):
    service = SectionTemplateService(SectionTemplateRepository(db))
    return await service.get_by_document_type(document_type_id)


@router.post("/{document_type_id}/section-templates", response_model=SectionTemplateResponse)
async def create_section_template(
    document_type_id: int,
    request: SectionTemplateCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    service = SectionTemplateService(SectionTemplateRepository(db))
    return await service.create(document_type_id, request)
