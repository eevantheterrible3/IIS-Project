from pydantic import BaseModel
from datetime import datetime


class DocumentListResponse(BaseModel):
    document_id: str
    name: str

class ProjectDocumentListResponse(BaseModel):
    document_id: str
    name: str
    document_type_name: str | None = None
    created_at: datetime | None = None
    status: str | None = None
    tags: list[str] = []
    author: str | None = None

class DocumentListItemResponse(BaseModel):
    document_id: str
    name: str
    user_prompt: str | None = None
    document_type_id: str | None = None
    document_type_name: str | None = None
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class DocumentCreateRequest(BaseModel):
    name: str
    document_type_id: str
    project_id: str
    user_prompt: str | None = None