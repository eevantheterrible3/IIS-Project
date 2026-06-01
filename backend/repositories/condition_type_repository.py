from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.condition_type import ConditionType


class ConditionTypeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self):
        result = await self.db.execute(
            select(ConditionType).order_by(ConditionType.name)
        )
        return result.scalars().all()

    async def get_by_id(self, condition_type_id: str):
        result = await self.db.execute(
            select(ConditionType).where(ConditionType.condition_type_id == condition_type_id)
        )
        return result.scalar_one_or_none()

    async def create(self, condition_type: ConditionType):
        self.db.add(condition_type)
        await self.db.commit()
        await self.db.refresh(condition_type)
        return condition_type

    async def update(self, condition_type: ConditionType):
        await self.db.commit()
        await self.db.refresh(condition_type)
        return condition_type

    async def delete(self, condition_type: ConditionType):
        await self.db.delete(condition_type)
        await self.db.commit()
