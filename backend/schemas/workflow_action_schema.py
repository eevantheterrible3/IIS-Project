from pydantic import BaseModel
from typing import Optional


class WorkflowActionCreateRequest(BaseModel):
    name: str
    type: Optional[str] = None
    description: Optional[str] = None


class WorkflowActionUpdateRequest(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None


class WorkflowActionResponse(BaseModel):
    action_id: str
    name: str
    type: Optional[str] = None
    description: Optional[str] = None
