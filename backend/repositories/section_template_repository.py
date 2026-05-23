from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.section_template import SectionTemplate


class SectionTemplateRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_document_type(self, document_type_id: int):
        result = await self.db.execute(
            select(SectionTemplate)
            .where(SectionTemplate.document_type_id == document_type_id)
            .order_by(SectionTemplate.order_index)
        )
        return result.scalars().all()

    async def get_by_id(self, section_template_id: int):
        result = await self.db.execute(
            select(SectionTemplate).where(SectionTemplate.section_template_id == section_template_id)
        )
        return result.scalar_one_or_none()

    async def create(self, section_template: SectionTemplate):
        self.db.add(section_template)
        await self.db.commit()
        await self.db.refresh(section_template)
        return section_template

    async def update(self, section_template: SectionTemplate):
        await self.db.commit()
        await self.db.refresh(section_template)
        return section_template

    async def delete(self, section_template: SectionTemplate):
        await self.db.delete(section_template)
        await self.db.commit()
