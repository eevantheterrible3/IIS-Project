from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from database import get_db
from models.user import User
from repositories.workflow_action_repository import WorkflowActionRepository
from schemas.workflow_action_schema import (
    WorkflowActionCreateRequest,
    WorkflowActionUpdateRequest,
    WorkflowActionResponse,
)
from services.workflow_action_service import WorkflowActionService

router = APIRouter(prefix="/workflow-actions", tags=["Workflow Actions"])


@router.get("", response_model=List[WorkflowActionResponse])
async def get_all_actions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkflowActionService(WorkflowActionRepository(db))
    return await service.get_all()


@router.get("/{action_id}", response_model=WorkflowActionResponse)
async def get_action(
    action_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkflowActionService(WorkflowActionRepository(db))
    return await service.get_by_id(action_id)


@router.post("", response_model=WorkflowActionResponse)
async def create_action(
    request: WorkflowActionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkflowActionService(WorkflowActionRepository(db))
    return await service.create(request)


@router.put("/{action_id}", response_model=WorkflowActionResponse)
async def update_action(
    action_id: str,
    request: WorkflowActionUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkflowActionService(WorkflowActionRepository(db))
    return await service.update(action_id, request)


@router.delete("/{action_id}")
async def delete_action(
    action_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkflowActionService(WorkflowActionRepository(db))
    return await service.delete(action_id)
