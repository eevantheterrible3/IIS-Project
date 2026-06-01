from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.task_workflow import TaskWorkflow


class TaskWorkflowRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self):
        result = await self.db.execute(
            select(TaskWorkflow).options(selectinload(TaskWorkflow.steps))
        )
        return result.scalars().all()

    async def get_by_id(self, workflow_id: str):
        result = await self.db.execute(
            select(TaskWorkflow)
            .where(TaskWorkflow.task_workflow_id == workflow_id)
            .options(selectinload(TaskWorkflow.steps))
        )
        return result.scalar_one_or_none()

    async def create(self, workflow: TaskWorkflow):
        self.db.add(workflow)
        await self.db.commit()
        await self.db.refresh(workflow)
        return workflow

    async def update(self, workflow: TaskWorkflow):
        await self.db.commit()
        await self.db.refresh(workflow)
        return workflow

    async def delete(self, workflow: TaskWorkflow):
        await self.db.delete(workflow)
        await self.db.commit()
