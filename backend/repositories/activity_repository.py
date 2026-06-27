from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.activity import Activity, ActivityType


class ActivityRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_activity(
        self,
        document_id: str,
        user_id: str,
        activity_type: ActivityType
    ):
        activity = Activity(
            document_id=document_id,
            user_id=user_id,
            type=activity_type
        )

        self.db.add(activity)
        await self.db.flush()

        return activity

    async def get_document_activities(self, document_id: str):
        result = await self.db.execute(
            select(Activity)
            .options(selectinload(Activity.user))
            .where(Activity.document_id == document_id)
            .order_by(Activity.date.desc())
        )

        return result.scalars().all()