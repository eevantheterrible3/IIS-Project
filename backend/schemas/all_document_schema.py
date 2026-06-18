from pydantic import BaseModel
from datetime import datetime


class DocumentListResponse(BaseModel):
    document_id: str
    name: str


class DocumentListItemResponse(BaseModel):
    document_id: str
    name: str
    user_prompt: str | None = None
    document_type_id: str | None = None
    document_type_name: str | None = None
    file_type: str | None = None
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class DocumentCreateRequest(BaseModel):
    name: str
    document_type_id: str
    project_id: str
    file_type: str | None = None
    user_prompt: str | None = None