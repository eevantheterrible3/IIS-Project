from pydantic import BaseModel
from typing import Optional

class ProjectListResponse(BaseModel):
    project_id: str
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


# ── Project Realization schemas ───────────────────────────────────────────────

class MemberResponse(BaseModel):
    user_id: str
    name: str
    last_name: str
    role: str | None


class SubtaskSummaryResponse(BaseModel):
    subtask_id: str
    name: str
    description: str | None
    status: str | None
    deadline: str | None
    assigned_user: str | None


class TaskResourceSummaryResponse(BaseModel):
    resource_id: str
    name: str
    resource_type: str | None
    quantity: int
    status: str | None


class TaskSummaryResponse(BaseModel):
    task_id: str
    name: str
    description: str | None
    priority: str | None
    status: str | None
    is_completed: bool
    is_late: bool
    deadline: str | None
    assigned_user: str | None
    assigned_user_id: str | None
    subtasks: list[SubtaskSummaryResponse]
    resources: list[TaskResourceSummaryResponse]


class ProjectStatsResponse(BaseModel):
    total: int
    completed: int
    late: int
    progress: int
    deadline: str | None


class ProjectWithManagerResponse(BaseModel):
    project_id: str
    name: str
    description: str | None
    status: str | None
    start_date: str | None
    end_date: str | None
    manager_name: str | None


class ProjectDetailResponse(BaseModel):
    project_id: str
    name: str
    description: str | None
    status: str | None
    start_date: str | None
    end_date: str | None
    is_manager: bool
    stats: ProjectStatsResponse
    members: list[MemberResponse]
    tasks: list[TaskSummaryResponse]