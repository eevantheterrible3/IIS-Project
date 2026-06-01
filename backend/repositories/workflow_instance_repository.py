from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.workflow import Workflow
from models.workflow_instance import WorkflowInstance


class WorkflowInstanceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _base_options(self):
        return [
            selectinload(WorkflowInstance.workflow).selectinload(Workflow.document_type),
            selectinload(WorkflowInstance.document),
            selectinload(WorkflowInstance.current_step),
            selectinload(WorkflowInstance.designated_user),
        ]

    async def get_all(self):
        result = await self.db.execute(
            select(WorkflowInstance)
            .options(*self._base_options())
            .order_by(WorkflowInstance.started_at.desc())
        )
        return result.scalars().all()

    async def get_by_id(self, instance_id: str):
        result = await self.db.execute(
            select(WorkflowInstance)
            .where(WorkflowInstance.instance_id == instance_id)
            .options(*self._base_options())
        )
        return result.scalar_one_or_none()

    async def get_by_document(self, document_id: str):
        result = await self.db.execute(
            select(WorkflowInstance)
            .where(WorkflowInstance.document_id == document_id)
            .options(*self._base_options())
            .order_by(WorkflowInstance.started_at.desc())
        )
        return result.scalars().all()

    async def create(self, instance: WorkflowInstance):
        self.db.add(instance)
        await self.db.commit()
        await self.db.refresh(instance)
        return instance

    async def update(self, instance: WorkflowInstance):
        await self.db.commit()
        await self.db.refresh(instance)
        return instance

    async def delete(self, instance: WorkflowInstance):
        await self.db.delete(instance)
        await self.db.commit()
