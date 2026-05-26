from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DocumentRatingCreateRequest(BaseModel):
    document_id: str
    score: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class DocumentRatingUpdateRequest(BaseModel):
    score: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None


class DocumentRatingResponse(BaseModel):
    document_rating_id: str
    document_id: str
    user_id: str
    user_name: Optional[str] = None
    score: int
    comment: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
