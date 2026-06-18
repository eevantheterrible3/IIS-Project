from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.activity import Activity


class ActivityRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, user_id=None, activity_type=None, document_id=None):
        query = (
            select(Activity)
            .options(selectinload(Activity.user), selectinload(Activity.document))
            .order_by(Activity.date.desc())
        )
        if user_id:
            query = query.where(Activity.user_id == user_id)
        if activity_type:
            query = query.where(Activity.type == activity_type)
        if document_id:
            query = query.where(Activity.document_id == document_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, activity: Activity):
        self.db.add(activity)
        await self.db.commit()
        return activity
