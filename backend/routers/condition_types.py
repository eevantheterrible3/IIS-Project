from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from database import get_db
from models.user import User
from repositories.condition_type_repository import ConditionTypeRepository
from schemas.condition_type_schema import (
    ConditionTypeCreateRequest,
    ConditionTypeUpdateRequest,
    ConditionTypeResponse,
)
from services.condition_type_service import ConditionTypeService

router = APIRouter(prefix="/condition-types", tags=["Condition Types"])


@router.get("", response_model=List[ConditionTypeResponse])
async def get_all_condition_types(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConditionTypeService(ConditionTypeRepository(db))
    return await service.get_all()


@router.get("/{condition_type_id}", response_model=ConditionTypeResponse)
async def get_condition_type(
    condition_type_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConditionTypeService(ConditionTypeRepository(db))
    return await service.get_by_id(condition_type_id)


@router.post("", response_model=ConditionTypeResponse)
async def create_condition_type(
    request: ConditionTypeCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConditionTypeService(ConditionTypeRepository(db))
    return await service.create(request)


@router.put("/{condition_type_id}", response_model=ConditionTypeResponse)
async def update_condition_type(
    condition_type_id: str,
    request: ConditionTypeUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConditionTypeService(ConditionTypeRepository(db))
    return await service.update(condition_type_id, request)


@router.delete("/{condition_type_id}")
async def delete_condition_type(
    condition_type_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ConditionTypeService(ConditionTypeRepository(db))
    return await service.delete(condition_type_id)
