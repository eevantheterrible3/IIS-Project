from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.document import Document


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_documents_by_project_id(self, project_id: int):
        result = await self.db.execute(
            select(Document).where(Document.project_id == project_id)
        )
        return result.scalars().all()