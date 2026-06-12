from datetime import datetime

from pydantic import BaseModel

from models.task import TaskPriority


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
