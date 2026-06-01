from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from database import get_db
from models.user import User
from repositories.workflow_has_action_repository import WorkflowHasActionRepository
from schemas.workflow_has_action_schema import (
    WorkflowHasActionCreateRequest,
    WorkflowHasActionUpdateRequest,
    WorkflowHasActionResponse,
)
from services.workflow_has_action_service import WorkflowHasActionService

router = APIRouter(prefix="/workflow-has-actions", tags=["Workflow Has Actions"])


@router.get("/workflow/{workflow_id}", response_model=List[WorkflowHasActionResponse])
async def get_actions_for_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkflowHasActionService(WorkflowHasActionRepository(db))
    return await service.get_by_workflow(workflow_id)


@router.get("/{workflow_id}/{action_id}", response_model=WorkflowHasActionResponse)
async def get_workflow_action_link(
    workflow_id: str,
    action_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkflowHasActionService(WorkflowHasActionRepository(db))
    return await service.get_by_id(workflow_id, action_id)


@router.post("", response_model=WorkflowHasActionResponse)
async def create_workflow_action_link(
    request: WorkflowHasActionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkflowHasActionService(WorkflowHasActionRepository(db))
    return await service.create(request)


@router.put("/{workflow_id}/{action_id}", response_model=WorkflowHasActionResponse)
async def update_workflow_action_link(
    workflow_id: str,
    action_id: str,
    request: WorkflowHasActionUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkflowHasActionService(WorkflowHasActionRepository(db))
    return await service.update(workflow_id, action_id, request)


@router.delete("/{workflow_id}/{action_id}")
async def delete_workflow_action_link(
    workflow_id: str,
    action_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkflowHasActionService(WorkflowHasActionRepository(db))
    return await service.delete(workflow_id, action_id)
