from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class WorkflowCreateRequest(BaseModel):
    name: str
    created_by: Optional[str] = None


class WorkflowUpdateRequest(BaseModel):
    name: Optional[str] = None


class WorkflowResponse(BaseModel):
    workflow_id: str
    name: str
    created_by: Optional[str] = None
    creator_name: Optional[str] = None
    created_at: Optional[datetime] = None
