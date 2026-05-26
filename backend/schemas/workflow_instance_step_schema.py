from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class WorkflowInstanceStepCreateRequest(BaseModel):
    instance_id: str
    action_id: str
    status: str = "pending"
    progress: int = Field(0, ge=0, le=100)
    assigned_user_id: Optional[str] = None
    note: Optional[str] = None


class WorkflowInstanceStepUpdateRequest(BaseModel):
    status: Optional[str] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    assigned_user_id: Optional[str] = None
    note: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class WorkflowInstanceStepResponse(BaseModel):
    instance_step_id: str
    instance_id: str
    action_id: str
    action_name: Optional[str] = None
    status: str
    progress: int
    assigned_user_id: Optional[str] = None
    assigned_user_name: Optional[str] = None
    note: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
