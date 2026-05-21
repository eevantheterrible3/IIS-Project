from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.resource import Resource


class ResourceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self):
        result = await self.db.execute(select(Resource))
        return result.scalars().all()

    async def get_by_id(self, resource_id: int):
        result = await self.db.execute(
            select(Resource).where(Resource.resource_id == resource_id)
        )
        return result.scalar_one_or_none()

    async def create(self, resource: Resource):
        self.db.add(resource)
        await self.db.commit()
        await self.db.refresh(resource)
        return resource

    async def update(self, resource: Resource):
        await self.db.commit()
        await self.db.refresh(resource)
        return resource

    async def delete(self, resource: Resource):
        await self.db.delete(resource)
        await self.db.commit()
