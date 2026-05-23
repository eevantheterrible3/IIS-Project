from pydantic import BaseModel
from datetime import datetime


class DocumentListResponse(BaseModel):
    document_id: int
    name: str


class DocumentListItemResponse(BaseModel):
    document_id: int
    name: str
    user_prompt: str | None = None
    document_type_id: int | None = None
    document_type_name: str | None = None
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class DocumentCreateRequest(BaseModel):
    name: str
    document_type_id: int
    project_id: int
    user_prompt: str | None = None