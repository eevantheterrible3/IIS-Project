from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.workflow_has_action import WorkflowHasAction


class WorkflowHasActionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_workflow(self, workflow_id: str):
        result = await self.db.execute(
            select(WorkflowHasAction)
            .where(WorkflowHasAction.workflow_id == workflow_id)
            .options(
                selectinload(WorkflowHasAction.action),
                selectinload(WorkflowHasAction.next_action_ref),
            )
        )
        return result.scalars().all()

    async def get_by_id(self, workflow_id: str, action_id: str):
        result = await self.db.execute(
            select(WorkflowHasAction)
            .where(
                WorkflowHasAction.workflow_id == workflow_id,
                WorkflowHasAction.action_id == action_id,
            )
            .options(
                selectinload(WorkflowHasAction.action),
                selectinload(WorkflowHasAction.next_action_ref),
            )
        )
        return result.scalar_one_or_none()

    async def create(self, link: WorkflowHasAction):
        self.db.add(link)
        await self.db.commit()
        await self.db.refresh(link)
        return link

    async def update(self, link: WorkflowHasAction):
        await self.db.commit()
        await self.db.refresh(link)
        return link

    async def delete(self, link: WorkflowHasAction):
        await self.db.delete(link)
        await self.db.commit()
