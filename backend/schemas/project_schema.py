from pydantic import BaseModel


class ProjectListResponse(BaseModel):
    project_id: int
    name: str
    description: str | None = None
    status: str
    role: str | None = None