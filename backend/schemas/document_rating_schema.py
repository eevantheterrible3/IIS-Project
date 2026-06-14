from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class RatingCreateRequest(BaseModel):
    score: int
    comment: Optional[str] = None


class RatingResponse(BaseModel):
    document_rating_id: str
    document_id: str
    score: int
    comment: str | None = None
    created_at: datetime | None = None
    document_name: str | None = None
    user_name: str | None = None
