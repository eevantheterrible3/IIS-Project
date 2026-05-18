from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import get_db
from models.user import User
from models.work import Work

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


def verify_password(plain_password: str, stored_password: str):
    return plain_password == stored_password


@router.post("/login")
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    result = await db.execute(
        select(Work)
        .where(Work.user_id == user.user_id)
        .options(
            selectinload(Work.project),
            selectinload(Work.role)
        )
    )

    works = result.scalars().all()

    projects = [
        {
            "project_id": work.project.project_id,
            "project_name": work.project.name,
            "role_id": work.role.role_id,
            "role_name": work.role.name
        }
        for work in works
    ]

    return {
        "user": {
            "user_id": user.user_id,
            "username": user.username,
            "name": user.name,
            "last_name": user.last_name,
            "email": user.email
        },
        "projects": projects
    }