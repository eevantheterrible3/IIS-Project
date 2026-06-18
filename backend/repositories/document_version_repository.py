from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.document_version import DocumentVersion


class DocumentVersionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_document(self, document_id: str):
        from models.workflow_instance_step import WorkflowInstanceStep
        result = await self.db.execute(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .options(
                selectinload(DocumentVersion.author),
                selectinload(DocumentVersion.instance_step).selectinload(WorkflowInstanceStep.action),
            )
            .order_by(DocumentVersion.version_number.desc())
        )
        return result.scalars().all()

    async def get_by_id(self, version_id: str):
        result = await self.db.execute(
            select(DocumentVersion)
            .where(DocumentVersion.document_version_id == version_id)
        )
        return result.scalar_one_or_none()

    async def get_latest_number(self, document_id: str) -> int:
        result = await self.db.execute(
            select(func.max(DocumentVersion.version_number))
            .where(DocumentVersion.document_id == document_id)
        )
        return result.scalar() or 0

    async def create(self, version: DocumentVersion):
        self.db.add(version)
        await self.db.commit()
        await self.db.refresh(version)
        return version
