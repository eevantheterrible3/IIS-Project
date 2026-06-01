from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.workflow_action import WorkflowAction


class WorkflowActionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self):
        result = await self.db.execute(
            select(WorkflowAction).order_by(WorkflowAction.name)
        )
        return result.scalars().all()

    async def get_by_id(self, action_id: str):
        result = await self.db.execute(
            select(WorkflowAction).where(WorkflowAction.action_id == action_id)
        )
        return result.scalar_one_or_none()

    async def create(self, action: WorkflowAction):
        self.db.add(action)
        await self.db.commit()
        await self.db.refresh(action)
        return action

    async def update(self, action: WorkflowAction):
        await self.db.commit()
        await self.db.refresh(action)
        return action

    async def delete(self, action: WorkflowAction):
        await self.db.delete(action)
        await self.db.commit()
