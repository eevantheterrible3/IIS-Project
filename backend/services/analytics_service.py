from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from repositories.llm_usage_log_repository import LLMUsageLogRepository


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.repo = LLMUsageLogRepository(db)

    async def get_dashboard(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        document_type_id: Optional[str] = None,
        generation_type: Optional[str] = None,
        user_id: Optional[str] = None,
        recent_limit: int = 20,
    ) -> dict:
        filters = dict(
            start=start,
            end=end,
            document_type_id=document_type_id,
            generation_type=generation_type,
            user_id=user_id,
        )
        return {
            "summary": await self.repo.summary(**filters),
            "time_series": await self.repo.time_series(**filters),
            "by_document_type": await self.repo.by_document_type(**filters),
            "by_model": await self.repo.by_model(**filters),
            "by_user": await self.repo.by_user(**filters),
            "recent": await self.repo.recent(limit=recent_limit, **filters),
        }
