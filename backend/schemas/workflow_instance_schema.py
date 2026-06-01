from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class WorkflowInstanceCreateRequest(BaseModel):
    workflow_id: str
    document_id: str
    designated_user_id: Optional[str] = None
    note: Optional[str] = None


class WorkflowInstanceUpdateRequest(BaseModel):
    current_step_id: Optional[str] = None
    designated_user_id: Optional[str] = None
    note: Optional[str] = None
    completed_at: Optional[datetime] = None


class WorkflowInstanceResponse(BaseModel):
    instance_id: str
    workflow_id: str
    workflow_name: Optional[str] = None
    document_type_name: Optional[str] = None
    document_id: str
    document_name: Optional[str] = None
    current_step_id: Optional[str] = None
    current_step_name: Optional[str] = None
    designated_user_id: Optional[str] = None
    designated_user_name: Optional[str] = None
    note: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
