from pydantic import BaseModel
from typing import Optional

UNSET = "__UNSET__"


class WorkflowHasActionCreateRequest(BaseModel):
    workflow_id: str
    action_id: str
    next_action: Optional[str] = None
    is_start_step: bool = False
    condition_id: Optional[str] = None


class WorkflowHasActionUpdateRequest(BaseModel):
    next_action: Optional[str] = UNSET
    is_start_step: Optional[bool] = None
    condition_id: Optional[str] = UNSET


class WorkflowHasActionResponse(BaseModel):
    workflow_id: str
    action_id: str
    action_name: Optional[str] = None
    next_action: Optional[str] = None
    next_action_name: Optional[str] = None
    is_start_step: bool
    condition_id: Optional[str] = None
