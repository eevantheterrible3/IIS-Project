from datetime import datetime

from pydantic import BaseModel

from models.task_resource import TaskResourceStatus


class CreateTaskResourceRequest(BaseModel):
    task_id: str
    resource_id: str
    quantity: int = 1
    reserved_from: datetime | None = None
    reserved_until: datetime | None = None


class UpdateTaskResourceRequest(BaseModel):
    quantity: int | None = None
    reserved_from: datetime | None = None
    reserved_until: datetime | None = None
    status: TaskResourceStatus | None = None


class TaskResourceResponse(BaseModel):
    task_id: str
    resource_id: str
    quantity: int
    reserved_from: datetime | None
    reserved_until: datetime | None
    status: TaskResourceStatus

    model_config = {"from_attributes": True}


class TaskResourceDetailResponse(BaseModel):
    resource_id: str
    name: str
    resource_type: str | None
    quantity: int
    reserved_from: str | None
    reserved_until: str | None
