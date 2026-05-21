from datetime import datetime

from pydantic import BaseModel


class CreateTaskStatusHistoryRequest(BaseModel):
    task_id: int
    subtask_id: int | None = None
    old_step_id: int | None = None
    new_step_id: int
    changed_by_user_id: int


class TaskStatusHistoryResponse(BaseModel):
    history_id: int
    task_id: int
    subtask_id: int | None
    old_step_id: int | None
    new_step_id: int
    changed_by_user_id: int
    changed_at: datetime

    model_config = {"from_attributes": True}
