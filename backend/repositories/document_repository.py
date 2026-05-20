from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.document import Document
from models.is_marked import IsMarked
from models.tag import Tag


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_documents_by_project_id(self, project_id: int):
        result = await self.db.execute(
            select(Document).where(Document.project_id == project_id)
        )
        return result.scalars().all()

    async def get_document_details(self, document_id: int):
        result = await self.db.execute(
            select(Document)
            .where(Document.document_id == document_id)
            .options(
                selectinload(Document.user),
                selectinload(Document.project),
                selectinload(Document.metadata_items),
                selectinload(Document.tags).selectinload(IsMarked.tag)
            )
        )

        return result.scalar_one_or_none()

    async def delete_document(self, document: Document):
        await self.db.delete(document)
        await self.db.commit()

    async def get_document_by_id(self, document_id: int):
        result = await self.db.execute(
            select(Document).where(Document.document_id == document_id)
        )
        return result.scalar_one_or_none()