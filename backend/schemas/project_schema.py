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


class HomeProjectItem(BaseModel):
    project_id: str
    name: str
    status: str | None
    member_count: int
    manager_name: str | None
    deadline: str | None
    task_total: int
    task_completed: int
    task_late: int
    progress: int


class HomeMyTask(BaseModel):
    task_id: str
    name: str
    project_name: str
    project_id: str
    status: str | None
    priority: str | None
    deadline: str | None
    is_late: bool
    is_completed: bool


class HomeResponse(BaseModel):
    stats_projects: int
    stats_active: int
    stats_late: int
    projects: list[HomeProjectItem]
    my_tasks: list[HomeMyTask]


class ReportWorkflowStep(BaseModel):
    step_name: str
    task_count: int


class ReportMember(BaseModel):
    name: str
    active_tasks: int
    completed_tasks: int


class ReportProjectItem(BaseModel):
    name: str
    task_total: int
    task_completed: int
    task_late: int
    progress: int
    deadline: str | None
    manager_name: str | None


class ReportResponse(BaseModel):
    generated_at: str
    stats_projects: int
    stats_total_tasks: int
    stats_completed: int
    stats_active: int
    stats_late: int
    projects: list[ReportProjectItem]
    workflow_steps: list[ReportWorkflowStep]
    members: list[ReportMember]