from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from repositories.task_workflow_repository import TaskWorkflowRepository
from repositories.task_workflow_step_repository import TaskWorkflowStepRepository
from services.task_workflow_service import TaskWorkflowService
from schemas.task_workflow_schema import CreateTaskWorkflowRequest, TaskWorkflowResponse

router = APIRouter(prefix="/workflows", tags=["Workflows"])


@router.get("/", response_model=List[TaskWorkflowResponse])
async def get_all_workflows(db: AsyncSession = Depends(get_db)):
    service = TaskWorkflowService(TaskWorkflowRepository(db), TaskWorkflowStepRepository(db))
    return await service.get_all()


@router.post("/", response_model=TaskWorkflowResponse)
async def create_workflow(data: CreateTaskWorkflowRequest, db: AsyncSession = Depends(get_db)):
    service = TaskWorkflowService(TaskWorkflowRepository(db), TaskWorkflowStepRepository(db))
    return await service.create(data)


@router.put("/{workflow_id}", response_model=TaskWorkflowResponse)
async def update_workflow(workflow_id: str, name: str, db: AsyncSession = Depends(get_db)):
    service = TaskWorkflowService(TaskWorkflowRepository(db), TaskWorkflowStepRepository(db))
    return await service.update(workflow_id, name)


@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: str, db: AsyncSession = Depends(get_db)):
    service = TaskWorkflowService(TaskWorkflowRepository(db), TaskWorkflowStepRepository(db))
    return await service.delete(workflow_id)
