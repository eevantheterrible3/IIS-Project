from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from database import get_db
from models.user import User
from repositories.condition_repository import ConditionRepository
from schemas.condition_schema import (
    ConditionCreateRequest,
    ConditionUpdateRequest,
    ConditionResponse,
)
from services.condition_service import ConditionService

router = APIRouter(prefix="/conditions", tags=["Conditions"])


@router.get("", response_model=List[ConditionResponse])
async def get_all_conditions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConditionService(ConditionRepository(db))
    return await service.get_all()


@router.get("/{condition_id}", response_model=ConditionResponse)
async def get_condition(
    condition_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConditionService(ConditionRepository(db))
    return await service.get_by_id(condition_id)


@router.post("", response_model=ConditionResponse)
async def create_condition(
    request: ConditionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConditionService(ConditionRepository(db))
    return await service.create(request)


@router.put("/{condition_id}", response_model=ConditionResponse)
async def update_condition(
    condition_id: str,
    request: ConditionUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConditionService(ConditionRepository(db))
    return await service.update(condition_id, request)


@router.delete("/{condition_id}")
async def delete_condition(
    condition_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConditionService(ConditionRepository(db))
    return await service.delete(condition_id)
