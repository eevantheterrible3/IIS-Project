from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.workflow import Workflow


class WorkflowRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self):
        result = await self.db.execute(
            select(Workflow)
            .options(selectinload(Workflow.creator))
            .order_by(Workflow.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_id(self, workflow_id: str):
        result = await self.db.execute(
            select(Workflow)
            .where(Workflow.workflow_id == workflow_id)
            .options(selectinload(Workflow.creator))
        )
        return result.scalar_one_or_none()

    async def create(self, workflow: Workflow):
        self.db.add(workflow)
        await self.db.commit()
        await self.db.refresh(workflow)
        return workflow

    async def update(self, workflow: Workflow):
        await self.db.commit()
        await self.db.refresh(workflow)
        return workflow

    async def delete(self, workflow: Workflow):
        await self.db.delete(workflow)
        await self.db.commit()
