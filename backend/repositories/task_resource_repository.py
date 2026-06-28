from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.task_resource import TaskResource


class TaskResourceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_task(self, task_id: str):
        result = await self.db.execute(
            select(TaskResource).where(TaskResource.task_id == task_id)
        )
        return result.scalars().all()

    async def get_by_ids(self, task_id: str, resource_id: str):
        result = await self.db.execute(
            select(TaskResource).where(
                TaskResource.task_id == task_id,
                TaskResource.resource_id == resource_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_resource(self, resource_id: str):
        result = await self.db.execute(
            select(TaskResource).where(TaskResource.resource_id == resource_id)
        )
        return result.scalars().all()

    async def get_by_resource_and_period(self, resource_id: str, reserved_from: datetime, reserved_until: datetime):
        result = await self.db.execute(
            select(TaskResource).where(
                TaskResource.resource_id == resource_id,
                TaskResource.reserved_from <= reserved_until,
                TaskResource.reserved_until >= reserved_from,
            )
        )
        return result.scalars().all()

    async def get_all_with_resource(self):
        result = await self.db.execute(
            select(TaskResource).options(selectinload(TaskResource.resource))
        )
        return result.scalars().all()

    async def create(self, task_resource: TaskResource):
        self.db.add(task_resource)
        await self.db.commit()
        await self.db.refresh(task_resource)
        return task_resource

    async def update(self, task_resource: TaskResource):
        await self.db.commit()
        await self.db.refresh(task_resource)
        return task_resource

    async def delete(self, task_resource: TaskResource):
        await self.db.delete(task_resource)
        await self.db.commit()
