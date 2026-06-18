from pydantic import BaseModel
from datetime import datetime


class ActivityResponse(BaseModel):
    activity_id: str
    document_id: str
    document_name: str | None = None
    user_id: str
    user_name: str | None = None
    type: str
    date: datetime | None = None
