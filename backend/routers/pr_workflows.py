from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from database import get_db
from models.user import User
from repositories.task_workflow_repository import TaskWorkflowRepository
from repositories.task_workflow_step_repository import TaskWorkflowStepRepository
from schemas.task_workflow_schema import (
    CreateTaskWorkflowRequest,
    UpdateTaskWorkflowRequest,
    WorkflowWithOrderedStepsResponse,
)
from services.task_workflow_service import TaskWorkflowService

router = APIRouter(prefix="/project-realization/workflows", tags=["PR Workflows"])


def _service(db: AsyncSession) -> TaskWorkflowService:
    return TaskWorkflowService(TaskWorkflowRepository(db), TaskWorkflowStepRepository(db))


@router.get("", response_model=list[WorkflowWithOrderedStepsResponse])
async def get_workflows(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _service(db).get_all_with_ordered_steps()


@router.post("", response_model=WorkflowWithOrderedStepsResponse)
async def create_workflow(
    data: CreateTaskWorkflowRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _service(db).create_for_pr(data, current_user.user_id)


@router.put("/{workflow_id}", response_model=WorkflowWithOrderedStepsResponse)
async def update_workflow(
    workflow_id: str,
    data: UpdateTaskWorkflowRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _service(db).update_full(workflow_id, data)


@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await _service(db).delete(workflow_id)
