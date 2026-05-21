from datetime import datetime

from pydantic import BaseModel

from models.subtask import SubtaskStatus


class CreateSubtaskRequest(BaseModel):
    task_id: int
    name: str
    description: str | None = None
    deadline: datetime | None = None
    assigned_user_id: int | None = None


class UpdateSubtaskRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    deadline: datetime | None = None
    current_status: SubtaskStatus | None = None
    assigned_user_id: int | None = None


class SubtaskResponse(BaseModel):
    subtask_id: int
    task_id: int
    name: str
    description: str | None
    deadline: datetime | None
    current_status: SubtaskStatus
    assigned_user_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}
