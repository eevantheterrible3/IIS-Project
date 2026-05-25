from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.document_section import DocumentSection


class DocumentSectionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_document(self, document_id: int):
        result = await self.db.execute(
            select(DocumentSection)
            .where(DocumentSection.document_id == document_id)
            .options(selectinload(DocumentSection.section_template))
            .order_by(DocumentSection.order_index)
        )
        return result.scalars().all()

    async def get_by_id(self, document_section_id: int):
        result = await self.db.execute(
            select(DocumentSection)
            .where(DocumentSection.document_section_id == document_section_id)
            .options(selectinload(DocumentSection.section_template))
        )
        return result.scalar_one_or_none()

    async def create(self, section: DocumentSection):
        self.db.add(section)
        await self.db.commit()
        await self.db.refresh(section)
        return section

    async def update(self, section: DocumentSection):
        await self.db.commit()
        await self.db.refresh(section)
        return section
