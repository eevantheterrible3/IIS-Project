from datetime import datetime

from pydantic import BaseModel

from models.task import TaskPriority


class CreateTaskRequest(BaseModel):
    name: str
    description: str | None = None
    priority: TaskPriority | None = None
    task_workflow_id: int
    deadline: datetime | None = None
    assigned_user_id: int | None = None
    project_id: int


class UpdateTaskRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    priority: TaskPriority | None = None
    deadline: datetime | None = None
    assigned_user_id: int | None = None
    current_step_id: int | None = None


class TaskListResponse(BaseModel):
    task_id: int
    name: str
    priority: TaskPriority | None
    deadline: datetime | None
    current_step_id: int | None
    assigned_user_id: int | None

    model_config = {"from_attributes": True}


class TaskDetailResponse(BaseModel):
    task_id: int
    name: str
    description: str | None
    priority: TaskPriority | None
    task_workflow_id: int
    current_step_id: int | None
    deadline: datetime | None
    assigned_user_id: int | None
    project_id: int
    created_at: datetime
    last_updated_at: datetime

    model_config = {"from_attributes": True}
