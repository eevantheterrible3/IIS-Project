from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from repositories.section_template_repository import SectionTemplateRepository
from services.section_template_service import SectionTemplateService
from schemas.section_template_schema import SectionTemplateUpdateRequest, SectionTemplateResponse

router = APIRouter(prefix="/section-templates", tags=["Section Templates"])


@router.put("/{section_template_id}", response_model=SectionTemplateResponse)
async def update_section_template(
    section_template_id: int,
    request: SectionTemplateUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    service = SectionTemplateService(SectionTemplateRepository(db))
    return await service.update(section_template_id, request)


@router.delete("/{section_template_id}")
async def delete_section_template(section_template_id: int, db: AsyncSession = Depends(get_db)):
    service = SectionTemplateService(SectionTemplateRepository(db))
    return await service.delete(section_template_id)
