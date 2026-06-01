from pydantic import BaseModel
from typing import Optional


class ConditionTypeCreateRequest(BaseModel):
    name: str


class ConditionTypeUpdateRequest(BaseModel):
    name: Optional[str] = None


class ConditionTypeResponse(BaseModel):
    condition_type_id: str
    name: str
