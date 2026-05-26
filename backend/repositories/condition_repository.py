from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.condition import Condition


class ConditionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self):
        result = await self.db.execute(
            select(Condition)
            .options(
                selectinload(Condition.condition_type),
                selectinload(Condition.document_type),
                selectinload(Condition.role),
            )
        )
        return result.scalars().all()

    async def get_by_id(self, condition_id: str):
        result = await self.db.execute(
            select(Condition)
            .where(Condition.condition_id == condition_id)
            .options(
                selectinload(Condition.condition_type),
                selectinload(Condition.document_type),
                selectinload(Condition.role),
            )
        )
        return result.scalar_one_or_none()

    async def create(self, condition: Condition):
        self.db.add(condition)
        await self.db.commit()
        await self.db.refresh(condition)
        return condition

    async def update(self, condition: Condition):
        await self.db.commit()
        await self.db.refresh(condition)
        return condition

    async def delete(self, condition: Condition):
        await self.db.delete(condition)
        await self.db.commit()
