from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from database import get_db
from models.user import User
from repositories.project_repository import ProjectRepository
from repositories.subtask_repository import SubtaskRepository
from repositories.task_repository import TaskRepository
from services.subtask_service import SubtaskService
from services.task_service import TaskService
from schemas.subtask_schema import CreateSubtaskRequest, UpdateSubtaskRequest
from schemas.task_schema import (
    CreateTaskRequest,
    TaskDetailResponse,
    TaskFullDetailResponse,
    TaskListResponse,
    UpdateTaskRequest,
)

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


# ── Task detail (Project Realization) ─────────────────────────────────────────

async def _load_task_and_project(task_id: str, db: AsyncSession):
    task = await TaskRepository(db).get_detail_with_relations(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    project = await ProjectRepository(db).get_by_id_with_members(task.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return task, project


@router.get("/{task_id}/detail", response_model=TaskFullDetailResponse)
async def get_task_detail(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return the full task detail for the task page."""
    uid = current_user.user_id
    task, project = await _load_task_and_project(task_id, db)
    service = TaskService(TaskRepository(db))
    is_admin = await ProjectRepository(db).is_user_admin(uid)
    service.ensure_can_view(project, uid, is_admin)
    return service.build_detail(task, project, uid)


@router.put("/{task_id}/advance", response_model=TaskFullDetailResponse)
async def advance_task_step(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Move the task to the next workflow step (PM or assigned member only)."""
    uid = current_user.user_id
    task, project = await _load_task_and_project(task_id, db)
    service = TaskService(TaskRepository(db))
    await service.advance_step(task, project, uid)
    db.expire_all()
    task, project = await _load_task_and_project(task_id, db)
    return service.build_detail(task, project, uid)


@router.put("/{task_id}/subtasks/{subtask_id}/status", response_model=TaskFullDetailResponse)
async def set_subtask_status(
    task_id: str,
    subtask_id: str,
    data: UpdateSubtaskRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Set a subtask's status (PM or assigned member only)."""
    uid = current_user.user_id
    task, project = await _load_task_and_project(task_id, db)
    service = TaskService(TaskRepository(db))
    service.ensure_can_change_status(task, project, uid)

    subtask_service = SubtaskService(SubtaskRepository(db))
    subtask = await subtask_service.get_by_id(subtask_id)
    if subtask.task_id != task_id:
        raise HTTPException(status_code=400, detail="Subtask does not belong to this task")
    await subtask_service.update(subtask_id, data)

    db.expire_all()
    task, project = await _load_task_and_project(task_id, db)
    return service.build_detail(task, project, uid)


@router.put("/{task_id}/edit", response_model=TaskFullDetailResponse)
async def edit_task(
    task_id: str,
    data: UpdateTaskRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Edit task fields (project manager only)."""
    uid = current_user.user_id
    task, project = await _load_task_and_project(task_id, db)
    service = TaskService(TaskRepository(db))
    if not service._is_manager(project, uid):
        raise HTTPException(status_code=403, detail="Only the project manager can edit tasks.")
    await service.update(task_id, data)
    db.expire_all()
    task, project = await _load_task_and_project(task_id, db)
    return service.build_detail(task, project, uid)


@router.post("/{task_id}/subtasks", response_model=TaskFullDetailResponse, status_code=201)
async def add_subtask(
    task_id: str,
    data: CreateSubtaskRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a new subtask to the task (project manager only)."""
    uid = current_user.user_id
    task, project = await _load_task_and_project(task_id, db)
    service = TaskService(TaskRepository(db))
    if not service._is_manager(project, uid):
        raise HTTPException(status_code=403, detail="Only the project manager can add subtasks.")

    subtask_service = SubtaskService(SubtaskRepository(db))
    await subtask_service.create(data)

    db.expire_all()
    task, project = await _load_task_and_project(task_id, db)
    return service.build_detail(task, project, uid)
