from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.task_workflow_step import TaskWorkflowStep


class TaskWorkflowStepRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, step_id: str):
        result = await self.db.execute(
            select(TaskWorkflowStep).where(TaskWorkflowStep.step_id == step_id)
        )
        return result.scalar_one_or_none()

    async def create_and_flush(self, step: TaskWorkflowStep):
        self.db.add(step)
        await self.db.flush()
        return step

    async def commit(self):
        await self.db.commit()
