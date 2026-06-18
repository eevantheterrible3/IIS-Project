from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.workflow_instance import WorkflowInstance
from models.workflow_instance_step import WorkflowInstanceStep
from models.workflow_has_action import WorkflowHasAction


class WorkflowInstanceStepRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_instance(self, instance_id: str):
        result = await self.db.execute(
            select(WorkflowInstanceStep)
            .join(WorkflowInstance, WorkflowInstanceStep.instance_id == WorkflowInstance.instance_id)
            .outerjoin(WorkflowHasAction, and_(
                WorkflowHasAction.workflow_id == WorkflowInstance.workflow_id,
                WorkflowHasAction.action_id == WorkflowInstanceStep.action_id,
            ))
            .where(WorkflowInstanceStep.instance_id == instance_id)
            .options(
                selectinload(WorkflowInstanceStep.action),
                selectinload(WorkflowInstanceStep.assigned_user),
                
            )
            .order_by(WorkflowHasAction.step_order)
        )
        return result.scalars().all()

    async def get_by_id(self, instance_step_id: str):
        result = await self.db.execute(
            select(WorkflowInstanceStep)
            .where(WorkflowInstanceStep.instance_step_id == instance_step_id)
            .options(
                selectinload(WorkflowInstanceStep.action),
                selectinload(WorkflowInstanceStep.assigned_user),
                selectinload(WorkflowInstanceStep.instance),
            )
        )
        return result.scalar_one_or_none()

    async def create(self, step: WorkflowInstanceStep):
        self.db.add(step)
        await self.db.commit()
        await self.db.refresh(step)
        return step

    async def update(self, step: WorkflowInstanceStep):
        await self.db.commit()
        await self.db.refresh(step)
        return step

    async def delete(self, step: WorkflowInstanceStep):
        await self.db.delete(step)
        await self.db.commit()
