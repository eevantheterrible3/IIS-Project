from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CommentCreateRequest(BaseModel):
    document_id: str
    version_id: Optional[str] = None
    content: str


class CommentResponse(BaseModel):
    comment_id: str
    document_id: str
    version_id: str | None = None
    user_id: str
    user_name: str | None = None
    content: str
    created_at: datetime | None = None
