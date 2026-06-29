from datetime import datetime

from pydantic import BaseModel

from models.task import TaskPriority
from schemas.task_status_history_schema import TaskHistoryDetailResponse
from schemas.task_resource_schema import TaskResourceDetailResponse


class CreateTaskRequest(BaseModel):
    name: str
    description: str | None = None
    priority: TaskPriority | None = None
    task_workflow_id: str
    deadline: datetime | None = None
    assigned_user_id: str | None = None
    project_id: str


class UpdateTaskRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    priority: TaskPriority | None = None
    deadline: datetime | None = None
    assigned_user_id: str | None = None
    current_step_id: str | None = None


class TaskListResponse(BaseModel):
    task_id: str
    name: str
    priority: TaskPriority | None
    deadline: datetime | None
    current_step_id: str | None
    assigned_user_id: str | None

    model_config = {"from_attributes": True}


class TaskDetailResponse(BaseModel):
    task_id: str
    name: str
    description: str | None
    priority: TaskPriority | None
    task_workflow_id: str
    current_step_id: str | None
    deadline: datetime | None
    assigned_user_id: str | None
    project_id: str
    created_at: datetime
    last_updated_at: datetime

    model_config = {"from_attributes": True}


# ── Project Realization schemas ───────────────────────────────────────────────

class CreateTaskResourceRequest(BaseModel):
    resource_id: str
    quantity: int = 1
    reserved_from: str | None = None
    reserved_until: str | None = None


class CreateTaskWithResourcesRequest(BaseModel):
    name: str
    description: str | None = None
    task_workflow_id: str
    priority: str | None = None
    assigned_user_id: str | None = None
    deadline: str | None = None
    subtasks: list = []
    resources: list[CreateTaskResourceRequest] = []


# ── Task detail (Project Realization) ─────────────────────────────────────────

class TaskStepResponse(BaseModel):
    step_id: str
    status_name: str
    is_first: bool
    is_last: bool
    is_current: bool


class TaskSubtaskResponse(BaseModel):
    subtask_id: str
    name: str
    description: str | None
    status: str | None
    deadline: str | None
    assigned_user: str | None
    assigned_user_id: str | None


class TaskFullDetailResponse(BaseModel):
    task_id: str
    project_id: str
    project_name: str
    name: str
    description: str | None
    priority: str | None
    status: str | None
    deadline: str | None
    created_at: str | None
    assigned_user: str | None
    assigned_user_id: str | None
    is_completed: bool
    is_late: bool
    steps: list[TaskStepResponse]
    current_step_id: str | None
    next_step_id: str | None
    next_step_name: str | None
    subtasks: list[TaskSubtaskResponse]
    resources: list[TaskResourceDetailResponse]
    history: list[TaskHistoryDetailResponse]
    progress_done: int
    progress_total: int
    progress_percent: int
    can_change_status: bool
    is_manager: bool
