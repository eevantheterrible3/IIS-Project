from datetime import datetime

from pydantic import BaseModel


class CreateTaskStatusHistoryRequest(BaseModel):
    task_id: str
    subtask_id: str | None = None
    old_step_id: str | None = None
    new_step_id: str
    changed_by_user_id: str


class TaskStatusHistoryResponse(BaseModel):
    history_id: str
    task_id: str
    subtask_id: str | None
    old_step_id: str | None
    new_step_id: str
    changed_by_user_id: str
    changed_at: datetime

    model_config = {"from_attributes": True}


class TaskHistoryDetailResponse(BaseModel):
    old_step: str | None
    new_step: str
    changed_by: str
    changed_at: str
