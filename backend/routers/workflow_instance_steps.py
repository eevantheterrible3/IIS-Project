from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from database import get_db
from models.user import User
from repositories.workflow_instance_step_repository import WorkflowInstanceStepRepository
from schemas.workflow_instance_step_schema import (
    WorkflowInstanceStepCreateRequest,
    WorkflowInstanceStepUpdateRequest,
    WorkflowInstanceStepResponse,
)
from services.workflow_instance_step_service import WorkflowInstanceStepService

router = APIRouter(prefix="/workflow-instance-steps", tags=["Workflow Instance Steps"])


@router.get("/instance/{instance_id}", response_model=List[WorkflowInstanceStepResponse])
async def get_steps_for_instance(
    instance_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkflowInstanceStepService(WorkflowInstanceStepRepository(db))
    return await service.get_by_instance(instance_id)


@router.get("/{instance_step_id}", response_model=WorkflowInstanceStepResponse)
async def get_step(
    instance_step_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkflowInstanceStepService(WorkflowInstanceStepRepository(db))
    return await service.get_by_id(instance_step_id)


@router.post("", response_model=WorkflowInstanceStepResponse)
async def create_step(
    request: WorkflowInstanceStepCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkflowInstanceStepService(WorkflowInstanceStepRepository(db))
    return await service.create(request)


@router.put("/{instance_step_id}", response_model=WorkflowInstanceStepResponse)
async def update_step(
    instance_step_id: str,
    request: WorkflowInstanceStepUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkflowInstanceStepService(WorkflowInstanceStepRepository(db))
    return await service.update(instance_step_id, request)


@router.delete("/{instance_step_id}")
async def delete_step(
    instance_step_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkflowInstanceStepService(WorkflowInstanceStepRepository(db))
    return await service.delete(instance_step_id)
