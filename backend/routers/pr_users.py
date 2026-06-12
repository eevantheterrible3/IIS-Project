from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from database import get_db
from models.user import User

router = APIRouter(prefix="/project-realization/users", tags=["PR Users"])


@router.get("")
async def get_all_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return [
        {"user_id": u.user_id, "name": u.name, "last_name": u.last_name, "email": u.email}
        for u in users
    ]
