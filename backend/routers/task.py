from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from repositories.task_repository import TaskRepository
from services.task_service import TaskService
from schemas.task_schema import CreateTaskRequest, UpdateTaskRequest, TaskListResponse, TaskDetailResponse

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/", response_model=List[TaskListResponse])
async def get_tasks(project_id: str = Query(...), db: AsyncSession = Depends(get_db)):
    service = TaskService(TaskRepository(db))
    return await service.get_by_project(project_id)


@router.get("/{task_id}", response_model=TaskDetailResponse)
async def get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    service = TaskService(TaskRepository(db))
    return await service.get_by_id(task_id)


@router.post("/", response_model=TaskDetailResponse)
async def create_task(data: CreateTaskRequest, db: AsyncSession = Depends(get_db)):
    service = TaskService(TaskRepository(db))
    return await service.create(data)


@router.put("/{task_id}", response_model=TaskDetailResponse)
async def update_task(task_id: str, data: UpdateTaskRequest, db: AsyncSession = Depends(get_db)):
    service = TaskService(TaskRepository(db))
    return await service.update(task_id, data)


@router.delete("/{task_id}")
async def delete_task(task_id: str, db: AsyncSession = Depends(get_db)):
    service = TaskService(TaskRepository(db))
    return await service.delete(task_id)
