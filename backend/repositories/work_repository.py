from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.role import Role
from models.work import Work


class WorkRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_role_by_name(self, name: str) -> Role | None:
        result = await self.db.execute(select(Role).where(Role.name == name))
        return result.scalars().first()

    async def add(self, work: Work):
        self.db.add(work)
        await self.db.commit()

    async def delete(self, work: Work):
        await self.db.delete(work)
        await self.db.commit()
