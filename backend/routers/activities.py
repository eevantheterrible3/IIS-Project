from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from database import get_db
from models.user import User
from repositories.activity_repository import ActivityRepository
from schemas.activity_schema import ActivityResponse
from services.activity_service import ActivityService

router = APIRouter(prefix="/activities", tags=["Activities"])


@router.get("", response_model=List[ActivityResponse])
async def get_activities(
    user_id: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    document_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ActivityService(ActivityRepository(db))
    return await service.get_activities(user_id, type, document_id)
