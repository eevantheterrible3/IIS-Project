from pydantic import BaseModel
from typing import Optional

class ProjectListResponse(BaseModel):
    project_id: int
    name: str
    description: str | None = None
    status: str
    role: str | None = None

class ProjectCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "ACTIVE"
class ProjectUpdateRequest(BaseModel):
    name: str
    description: Optional[str] = None