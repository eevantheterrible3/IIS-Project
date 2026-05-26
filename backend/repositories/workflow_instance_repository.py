from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.workflow_instance import WorkflowInstance


class WorkflowInstanceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self):
        result = await self.db.execute(
            select(WorkflowInstance)
            .options(
                selectinload(WorkflowInstance.workflow),
                selectinload(WorkflowInstance.current_step),
                selectinload(WorkflowInstance.designated_user),
            )
            .order_by(WorkflowInstance.started_at.desc())
        )
        return result.scalars().all()

    async def get_by_id(self, instance_id: str):
        result = await self.db.execute(
            select(WorkflowInstance)
            .where(WorkflowInstance.instance_id == instance_id)
            .options(
                selectinload(WorkflowInstance.workflow),
                selectinload(WorkflowInstance.current_step),
                selectinload(WorkflowInstance.designated_user),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_document(self, document_id: str):
        result = await self.db.execute(
            select(WorkflowInstance)
            .where(WorkflowInstance.document_id == document_id)
            .options(
                selectinload(WorkflowInstance.workflow),
                selectinload(WorkflowInstance.current_step),
                selectinload(WorkflowInstance.designated_user),
            )
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
