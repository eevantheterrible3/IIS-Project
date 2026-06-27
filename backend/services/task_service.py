import uuid
from datetime import datetime

from fastapi import HTTPException

from models.task import Task
from schemas.task_schema import (
    CreateTaskRequest,
    CreateTaskWithResourcesRequest,
    TaskDetailResponse,
    TaskFullDetailResponse,
    TaskListResponse,
    TaskStepResponse,
    TaskSubtaskResponse,
    UpdateTaskRequest,
)
from services.task_workflow_service import TaskWorkflowService


class TaskService:
    def __init__(self, repository, task_resource_service=None):
        self.repository = repository
        self.task_resource_service = task_resource_service

    async def get_by_project(self, project_id: str) -> list[TaskListResponse]:
        tasks = await self.repository.get_by_project(project_id)
        return [TaskListResponse.model_validate(t) for t in tasks]

    async def get_by_id(self, task_id: str) -> TaskDetailResponse:
        task = await self.repository.get_by_id(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return TaskDetailResponse.model_validate(task)

    async def create(self, data: CreateTaskRequest) -> TaskDetailResponse:
        task = Task(
            name=data.name,
            description=data.description,
            priority=data.priority,
            task_workflow_id=data.task_workflow_id,
            deadline=data.deadline,
            assigned_user_id=data.assigned_user_id,
            project_id=data.project_id
        )
        result = await self.repository.create(task)
        return TaskDetailResponse.model_validate(result)

    async def update(self, task_id: int, data: UpdateTaskRequest) -> TaskDetailResponse:
        task = await self.repository.get_by_id(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        if data.name is not None:
            task.name = data.name
        if data.description is not None:
            task.description = data.description
        if data.priority is not None:
            task.priority = data.priority
        if data.deadline is not None:
            task.deadline = data.deadline
        if data.assigned_user_id is not None:
            task.assigned_user_id = data.assigned_user_id
        if data.current_step_id is not None:
            task.current_step_id = data.current_step_id
        result = await self.repository.update(task)
        return TaskDetailResponse.model_validate(result)

    async def delete(self, task_id: str):
        task = await self.repository.get_by_id(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        await self.repository.delete(task)
        return {"message": "Task deleted"}


    # ── Task detail (Project Realization) ─────────────────────────────────────

    def _is_manager(self, project, user_id: str) -> bool:
        return any(
            w.user_id == user_id and w.role and w.role.name == "PROJECT_MANAGER"
            for w in project.works
        )

    def can_change_status(self, task, project, user_id: str) -> bool:
        return self._is_manager(project, user_id) or task.assigned_user_id == user_id

    def ensure_can_view(self, project, user_id: str, is_admin: bool):
        if is_admin:
            return
        if not any(w.user_id == user_id for w in project.works):
            raise HTTPException(status_code=403, detail="You don't have access to this task.")

    def ensure_can_change_status(self, task, project, user_id: str):
        if not self.can_change_status(task, project, user_id):
            raise HTTPException(
                status_code=403,
                detail="Only the project manager or the assigned team member can do this.",
            )

    def build_detail(self, task, project, user_id: str) -> TaskFullDetailResponse:
        now = datetime.now()
        ordered = TaskWorkflowService._order_steps(task.workflow.steps if task.workflow else [])

        current = task.current_step
        is_completed = bool(current and current.is_last)
        is_late = bool(task.deadline and task.deadline < now and not is_completed)

        # find the next step in the ordered chain
        next_step = None
        if current and not current.is_last:
            for i, s in enumerate(ordered):
                if s.step_id == current.step_id and i + 1 < len(ordered):
                    next_step = ordered[i + 1]
                    break

        subtasks = [
            TaskSubtaskResponse(
                subtask_id=s.subtask_id,
                name=s.name,
                description=s.description,
                status=s.current_status.value if s.current_status else None,
                deadline=s.deadline.strftime("%d.%m.%Y") if s.deadline else None,
                assigned_user=(
                    f"{s.assigned_user.name} {s.assigned_user.last_name}"
                    if s.assigned_user else None
                ),
                assigned_user_id=s.assigned_user_id,
            )
            for s in task.subtasks
        ]
        done = sum(1 for s in task.subtasks if s.current_status and s.current_status.value == "done")
        total = len(task.subtasks)

        return TaskFullDetailResponse(
            task_id=task.task_id,
            project_id=task.project_id,
            project_name=task.project.name if task.project else "",
            name=task.name,
            description=task.description,
            priority=task.priority.value if task.priority else None,
            status=current.status_name if current else None,
            deadline=task.deadline.strftime("%d.%m.%Y") if task.deadline else None,
            created_at=task.created_at.strftime("%d.%m.%Y") if task.created_at else None,
            assigned_user=(
                f"{task.assigned_user.name} {task.assigned_user.last_name}"
                if task.assigned_user else None
            ),
            assigned_user_id=task.assigned_user_id,
            is_completed=is_completed,
            is_late=is_late,
            steps=[
                TaskStepResponse(
                    step_id=s.step_id,
                    status_name=s.status_name,
                    is_first=s.is_first,
                    is_last=s.is_last,
                    is_current=bool(current and s.step_id == current.step_id),
                )
                for s in ordered
            ],
            current_step_id=task.current_step_id,
            next_step_id=next_step.step_id if next_step else None,
            next_step_name=next_step.status_name if next_step else None,
            subtasks=subtasks,
            progress_done=done,
            progress_total=total,
            progress_percent=round(done / total * 100) if total else 0,
            can_change_status=self.can_change_status(task, project, user_id),
            is_manager=self._is_manager(project, user_id),
        )

    async def advance_step(self, task, project, user_id: str):
        self.ensure_can_change_status(task, project, user_id)

        ordered = TaskWorkflowService._order_steps(task.workflow.steps if task.workflow else [])
        current = task.current_step
        if current is None or current.is_last:
            raise HTTPException(status_code=400, detail="Task is already at the final step.")

        next_step = None
        for i, s in enumerate(ordered):
            if s.step_id == current.step_id and i + 1 < len(ordered):
                next_step = ordered[i + 1]
                break
        if next_step is None:
            raise HTTPException(status_code=400, detail="Task is already at the final step.")

        old_step_id = task.current_step_id
        task.current_step_id = next_step.step_id
        await self.repository.update(task)
        await self.repository.add_status_history(task.task_id, old_step_id, next_step.step_id, user_id)

    async def create_for_pr(self, project_id: str, data: CreateTaskWithResourcesRequest, first_step_id: str):
        deadline = datetime.strptime(data.deadline, "%Y-%m-%d") if data.deadline else None

        task = Task(
            task_id=str(uuid.uuid4()),
            name=data.name,
            description=data.description,
            priority=data.priority,
            task_workflow_id=data.task_workflow_id,
            current_step_id=first_step_id,
            deadline=deadline,
            assigned_user_id=data.assigned_user_id,
            project_id=project_id,
        )
        await self.repository.create(task)

        for res in data.resources:
            if res.resource_id:
                await self.task_resource_service.create_for_task(
                    task.task_id, res.resource_id, res.quantity, res.reserved_from, res.reserved_until
                )

        return {"task_id": task.task_id, "detail": "Task created"}
