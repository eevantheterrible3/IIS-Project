from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.subtask import Subtask


class SubtaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_task(self, task_id: int):
        result = await self.db.execute(
            select(Subtask).where(Subtask.task_id == task_id)
        )
        return result.scalars().all()

    async def get_by_id(self, subtask_id: int):
        result = await self.db.execute(
            select(Subtask).where(Subtask.subtask_id == subtask_id)
        )
        return result.scalar_one_or_none()

    async def create(self, subtask: Subtask):
        self.db.add(subtask)
        await self.db.commit()
        await self.db.refresh(subtask)
        return subtask

    async def update(self, subtask: Subtask):
        await self.db.commit()
        await self.db.refresh(subtask)
        return subtask

    async def delete(self, subtask: Subtask):
        await self.db.delete(subtask)
        await self.db.commit()
