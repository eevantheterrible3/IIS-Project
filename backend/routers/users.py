from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.user import User
from schemas.user_schema import UserResponse
from core.dependencies import get_current_user

router = APIRouter()


@router.get("", response_model=list[UserResponse])
async def get_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).order_by(User.name, User.last_name)
    )

    return result.scalars().all()