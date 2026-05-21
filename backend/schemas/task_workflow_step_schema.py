from pydantic import BaseModel


class CreateTaskWorkflowStepRequest(BaseModel):
    task_workflow_id: int
    status_name: str
    next_step_id: int | None = None
    is_first: bool = False
    is_last: bool = False


class TaskWorkflowStepResponse(BaseModel):
    step_id: int
    task_workflow_id: int
    status_name: str
    next_step_id: int | None
    is_first: bool
    is_last: bool

    model_config = {"from_attributes": True}
