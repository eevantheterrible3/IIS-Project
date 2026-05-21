from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.task import Task


class TaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_project(self, project_id: int):
        result = await self.db.execute(
            select(Task).where(Task.project_id == project_id)
        )
        return result.scalars().all()

    async def get_by_id(self, task_id: int):
        result = await self.db.execute(
            select(Task).where(Task.task_id == task_id)
        )
        return result.scalar_one_or_none()

    async def create(self, task: Task):
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def update(self, task: Task):
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def delete(self, task: Task):
        await self.db.delete(task)
        await self.db.commit()
