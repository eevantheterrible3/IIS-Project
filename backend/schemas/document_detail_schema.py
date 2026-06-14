from pydantic import BaseModel
from datetime import datetime


class DocumentMetadataResponse(BaseModel):
    name: str
    value: str | None = None


class DocumentTagResponse(BaseModel):
    name: str


class DocumentDetailResponse(BaseModel):
    document_id: str
    name: str
    status: str | None = None
    user_prompt: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    author: str
    project_name: str

    tags: list[DocumentTagResponse]
    metadata: list[DocumentMetadataResponse]
    project_id: str