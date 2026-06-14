from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.document_type import DocumentType


class DocumentTypeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self):
        result = await self.db.execute(
            select(DocumentType).options(selectinload(DocumentType.section_templates)).order_by(DocumentType.document_type_id)
        )
        return result.scalars().all()

    async def get_by_id(self, document_type_id: int):
        result = await self.db.execute(
            select(DocumentType)
            .where(DocumentType.document_type_id == document_type_id)
            .options(selectinload(DocumentType.section_templates))
        )
        return result.scalar_one_or_none()

    async def create(self, document_type: DocumentType):
        self.db.add(document_type)
        await self.db.commit()
        await self.db.refresh(document_type)
        return document_type

    async def update(self, document_type: DocumentType):
        await self.db.commit()
        await self.db.refresh(document_type)
        return document_type

    async def delete(self, document_type: DocumentType):
        await self.db.delete(document_type)
        await self.db.commit()
