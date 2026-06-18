from models.activity import Activity, ActivityType
from schemas.activity_schema import ActivityResponse


class ActivityService:
    def __init__(self, activity_repository):
        self.activity_repository = activity_repository

    async def get_activities(self, user_id=None, activity_type=None, document_id=None):
        activities = await self.activity_repository.get_all(user_id, activity_type, document_id)
        return [
            ActivityResponse(
                activity_id=a.activity_id,
                document_id=a.document_id,
                document_name=a.document.name if a.document else None,
                user_id=a.user_id,
                user_name=f"{a.user.name} {a.user.last_name}" if a.user else None,
                type=a.type.value,
                date=a.date,
            )
            for a in activities
        ]

    async def log_activity(self, document_id: str, user_id: str, activity_type: ActivityType):
        activity = Activity(document_id=document_id, user_id=user_id, type=activity_type)
        return await self.activity_repository.create(activity)
