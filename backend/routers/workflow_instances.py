from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from database import get_db
from models.user import User
from repositories.workflow_instance_repository import WorkflowInstanceRepository
from schemas.workflow_instance_schema import (
    WorkflowInstanceCreateRequest,
    WorkflowInstanceUpdateRequest,
    WorkflowInstanceResponse,
)
from services.workflow_instance_service import WorkflowInstanceService

router = APIRouter(prefix="/workflow-instances", tags=["Workflow Instances"])


@router.get("", response_model=List[WorkflowInstanceResponse])
async def get_all_instances(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkflowInstanceService(WorkflowInstanceRepository(db))
    return await service.get_all()


@router.get("/{instance_id}", response_model=WorkflowInstanceResponse)
async def get_instance(
    instance_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkflowInstanceService(WorkflowInstanceRepository(db))
    return await service.get_by_id(instance_id)


@router.get("/document/{document_id}", response_model=List[WorkflowInstanceResponse])
async def get_instances_for_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkflowInstanceService(WorkflowInstanceRepository(db))
    return await service.get_by_document(document_id)


@router.post("", response_model=WorkflowInstanceResponse)
async def create_instance(
    request: WorkflowInstanceCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkflowInstanceService(WorkflowInstanceRepository(db))
    return await service.create(request)


@router.put("/{instance_id}", response_model=WorkflowInstanceResponse)
async def update_instance(
    instance_id: str,
    request: WorkflowInstanceUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkflowInstanceService(WorkflowInstanceRepository(db))
    return await service.update(instance_id, request)


@router.delete("/{instance_id}")
async def delete_instance(
    instance_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkflowInstanceService(WorkflowInstanceRepository(db))
    return await service.delete(instance_id)
