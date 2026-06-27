from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from database import get_db
from models.user import User
from repositories.project_repository import ProjectRepository
from repositories.resource_repository import ResourceRepository
from repositories.task_repository import TaskRepository
from repositories.task_resource_repository import TaskResourceRepository
from repositories.task_workflow_repository import TaskWorkflowRepository
from repositories.work_repository import WorkRepository
from schemas.task_schema import CreateTaskWithResourcesRequest
from services.project_service import ProjectService
from services.task_resource_service import TaskResourceService
from services.task_service import TaskService
from services.work_service import WorkService

router = APIRouter(prefix="/project-realization/projects", tags=["PR Projects"])


@router.get("")
async def get_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(ProjectRepository(db))
    return await service.get_all_for_pr(current_user.user_id)


@router.get("/{project_id}")
async def get_project_detail(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tasks = await TaskRepository(db).get_by_project_with_relations(project_id)
    service = ProjectService(ProjectRepository(db))
    return await service.get_detail_for_pr(project_id, tasks, current_user.user_id)


@router.post("/{project_id}/members", status_code=201)
async def add_member(
    project_id: str,
    body: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkService(WorkRepository(db), ProjectRepository(db))
    return await service.add_member(project_id, body.get("user_id"), current_user.user_id)


@router.delete("/{project_id}/members/{user_id}")
async def remove_member(
    project_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkService(WorkRepository(db), ProjectRepository(db))
    return await service.remove_member(project_id, user_id, current_user.user_id)


@router.post("/{project_id}/tasks", status_code=201)
async def create_task(
    project_id: str,
    data: CreateTaskWithResourcesRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await ProjectRepository(db).get_by_id_with_members(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    work_service = WorkService(WorkRepository(db), ProjectRepository(db))
    if not work_service._is_manager(project, current_user.user_id):
        raise HTTPException(status_code=403, detail="Only the project manager can create tasks")

    workflow = await TaskWorkflowRepository(db).get_by_id(data.task_workflow_id)
    if not workflow:
        raise HTTPException(status_code=400, detail="Workflow not found")
    first_step = next((s for s in workflow.steps if s.is_first), None)
    if not first_step:
        raise HTTPException(status_code=400, detail="Workflow has no first step")

    task_resource_service = TaskResourceService(TaskResourceRepository(db), ResourceRepository(db))
    service = TaskService(TaskRepository(db), task_resource_service)
    return await service.create_for_pr(project_id, data, first_step.step_id)
