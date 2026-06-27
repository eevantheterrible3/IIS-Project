from datetime import datetime
from pydantic import BaseModel, ConfigDict

from models.activity import ActivityType


class ActivityUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    username: str | None = None
    name: str
    last_name: str
    email: str


class ActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    activity_id: str
    document_id: str
    user_id: str
    type: ActivityType
    date: datetime
    user: ActivityUserResponse