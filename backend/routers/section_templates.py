from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from database import get_db
from models.user import User
from repositories.section_template_repository import SectionTemplateRepository
from schemas.section_template_schema import SectionTemplateResponse, SectionTemplateUpdateRequest
from services.section_template_service import SectionTemplateService

router = APIRouter(prefix="/section-templates", tags=["Section Templates"])


@router.put("/{section_template_id}", response_model=SectionTemplateResponse)
async def update_section_template(
    section_template_id: str,
    request: SectionTemplateUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SectionTemplateService(SectionTemplateRepository(db))
    return await service.update(section_template_id, request)


@router.delete("/{section_template_id}")
async def delete_section_template(
    section_template_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = SectionTemplateService(SectionTemplateRepository(db))
    return await service.delete(section_template_id)
