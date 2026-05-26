from datetime import datetime

from pydantic import BaseModel

from schemas.task_workflow_step_schema import TaskWorkflowStepResponse


class StepInWorkflowRequest(BaseModel):
    status_name: str
    is_first: bool = False
    is_last: bool = False


class CreateTaskWorkflowRequest(BaseModel):
    name: str
    created_by: str
    steps: list[StepInWorkflowRequest] = []


class TaskWorkflowResponse(BaseModel):
    task_workflow_id: str
    name: str
    created_at: datetime
    created_by: str
    steps: list[TaskWorkflowStepResponse]

    model_config = {"from_attributes": True}
