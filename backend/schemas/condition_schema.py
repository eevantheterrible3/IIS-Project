from pydantic import BaseModel
from typing import Optional


class ConditionCreateRequest(BaseModel):
    condition_type_id: Optional[str] = None
    document_type_id: Optional[str] = None
    role_id: Optional[str] = None
    description: Optional[str] = None


class ConditionUpdateRequest(BaseModel):
    condition_type_id: Optional[str] = None
    document_type_id: Optional[str] = None
    role_id: Optional[str] = None
    description: Optional[str] = None


class ConditionResponse(BaseModel):
    condition_id: str
    condition_type_id: Optional[str] = None
    condition_type_name: Optional[str] = None
    document_type_id: Optional[str] = None
    document_type_name: Optional[str] = None
    role_id: Optional[str] = None
    role_name: Optional[str] = None
    description: Optional[str] = None
