from datetime import datetime

from pydantic import BaseModel

from models.subtask import SubtaskStatus


class CreateSubtaskRequest(BaseModel):
    task_id: str
    name: str
    description: str | None = None
    deadline: datetime | None = None
    assigned_user_id: str | None = None


class UpdateSubtaskRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    deadline: datetime | None = None
    current_status: SubtaskStatus | None = None
    assigned_user_id: str | None = None


class SubtaskResponse(BaseModel):
    subtask_id: str
    task_id: str
    name: str
    description: str | None
    deadline: datetime | None
    current_status: SubtaskStatus
    assigned_user_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
