from fastapi import APIRouter, Depends, HTTPException
from jose import JWTError
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    is_hashed,
    verify_password,
)
from database import get_db
from models.user import User
from models.work import Work

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    name: str
    last_name: str
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


def _user_dict(user: User) -> dict:
    return {
        "user_id": user.user_id,
        "username": user.username,
        "name": user.name,
        "last_name": user.last_name,
        "email": user.email,
    }


async def _load_projects(user_id: int, db: AsyncSession) -> list:
    result = await db.execute(
        select(Work)
        .where(Work.user_id == user_id)
        .options(selectinload(Work.project), selectinload(Work.role))
    )
    return [
        {
            "project_id": w.project.project_id,
            "project_name": w.project.name,
            "role_id": w.role.role_id,
            "role_name": w.role.name,
        }
        for w in result.scalars().all()
    ]


@router.post("/login")
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Upgrade plaintext passwords to bcrypt on first successful login
    if not is_hashed(user.password):
        user.password = hash_password(request.password)
        await db.commit()

    return {
        "access_token": create_access_token(user.user_id),
        "refresh_token": create_refresh_token(user.user_id),
        "token_type": "bearer",
        "user": _user_dict(user),
        "projects": await _load_projects(user.user_id, db),
    }


@router.post("/register")
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        username=request.username,
        name=request.name,
        last_name=request.last_name,
        email=request.email,
        password=hash_password(request.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return {
        "access_token": create_access_token(user.user_id),
        "refresh_token": create_refresh_token(user.user_id),
        "token_type": "bearer",
        "user": _user_dict(user),
        "projects": [],
    }


@router.post("/refresh")
async def refresh_token(request: RefreshRequest, db: AsyncSession = Depends(get_db)):
    exc = HTTPException(status_code=401, detail="Invalid or expired refresh token")
    try:
        payload = decode_token(request.refresh_token)
        if payload.get("type") != "refresh":
            raise exc
        user_id = payload.get("sub")
        if not user_id:
            raise exc
    except JWTError:
        raise exc

    result = await db.execute(select(User).where(User.user_id == int(user_id)))
    if not result.scalar_one_or_none():
        raise exc

    return {"access_token": create_access_token(int(user_id)), "token_type": "bearer"}
