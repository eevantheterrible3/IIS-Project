from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from database import get_db
from models.user import User
from schemas.analytics_schema import DashboardResponse
from services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def _naive_utc(dt: Optional[datetime]) -> Optional[datetime]:
    """The frontend sends ISO strings with a 'Z' (tz-aware), but created_at is a
    naive (UTC) timestamp column. Convert aware datetimes to naive UTC so the
    comparison doesn't fail."""
    if dt is not None and dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    start: Optional[datetime] = Query(None, description="Start of date range (inclusive)"),
    end: Optional[datetime] = Query(None, description="End of date range (inclusive)"),
    document_type_id: Optional[str] = Query(None),
    generation_type: Optional[str] = Query(None, description="generate | refine"),
    scope: str = Query("all", description="'all' for global usage, 'me' for current user only"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_id = current_user.user_id if scope == "me" else None
    service = AnalyticsService(db)
    return await service.get_dashboard(
        start=_naive_utc(start),
        end=_naive_utc(end),
        document_type_id=document_type_id,
        generation_type=generation_type,
        user_id=user_id,
    )
