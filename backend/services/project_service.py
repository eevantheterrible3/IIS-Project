from datetime import datetime

from fastapi import HTTPException

from models.project import Project, ProjectStatus
from schemas.project_schema import (
    MemberResponse,
    ProjectDetailResponse,
    ProjectListResponse,
    ProjectStatsResponse,
    ProjectWithManagerResponse,
    SubtaskSummaryResponse,
    TaskResourceSummaryResponse,
    TaskSummaryResponse,
)

class ProjectService:
    def __init__(self, project_repository):
        self.project_repository = project_repository

    async def get_projects_for_user(self, user_id: int) -> list[ProjectListResponse]:
        works = await self.project_repository.get_user_works(user_id)

        is_admin = any(work.role.name == "ADMIN" for work in works)

        if is_admin:
            projects = await self.project_repository.get_all_projects()

            return [
                ProjectListResponse(
                    project_id=project.project_id,
                    name=project.name,
                    description=project.description,
                    status=project.status.value,
                    role="ADMIN"
                )
                for project in projects
            ]

        return [
            ProjectListResponse(
                project_id=work.project.project_id,
                name=work.project.name,
                description=work.project.description,
                status=work.project.status.value,
                role=work.role.name
            )
            for work in works
        ]
    async def ensure_user_is_admin(self, user_id: int):
        is_admin = await self.project_repository.is_user_admin(user_id)

        if not is_admin:
            raise HTTPException(
                status_code=403,
                detail="Only administrators can manage projects"
            )
    async def delete_project(self, project_id: int, user_id: int):
        await self.ensure_user_is_admin(user_id)

        project = await self.project_repository.get_project_by_id(project_id)

        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        await self.project_repository.delete_project(project)

        return {"message": "Project deleted successfully"}

    async def create_project(self, request, user_id: int):
        await self.ensure_user_is_admin(user_id)

        project = Project(
            name=request.name,
            description=request.description,
            start_date=datetime.now(),
            end_date=None,
            status=ProjectStatus.ACTIVE
        )

        return await self.project_repository.create_project(project)

    # ── Project Realization methods ───────────────────────────────────────────

    def _is_manager(self, project, user_id: str) -> bool:
        return any(
            w.user_id == user_id and w.role and w.role.name == "PROJECT_MANAGER"
            for w in project.works
        )

    async def get_all_for_pr(self) -> list[ProjectWithManagerResponse]:
        projects = await self.project_repository.get_all_with_members()
        result = []
        for p in projects:
            manager = next(
                (w.user for w in p.works if w.role and w.role.name == "PROJECT_MANAGER"),
                None,
            )
            result.append(ProjectWithManagerResponse(
                project_id=p.project_id,
                name=p.name,
                description=p.description,
                status=p.status.value if p.status else None,
                start_date=p.start_date.strftime("%d.%m.%y") if p.start_date else None,
                end_date=p.end_date.strftime("%d.%m.%y") if p.end_date else None,
                manager_name=f"{manager.name} {manager.last_name[0]}." if manager else None,
            ))
        return result

    async def get_detail_for_pr(self, project_id: str, tasks: list, current_user_id: str) -> ProjectDetailResponse:
        project = await self.project_repository.get_by_id_with_members(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        now = datetime.now()
        total = len(tasks)
        completed = sum(1 for t in tasks if t.current_step and t.current_step.is_last)
        late = sum(
            1 for t in tasks
            if t.deadline and t.deadline < now
            and not (t.current_step and t.current_step.is_last)
        )
        progress = round(completed / total * 100) if total else 0
        project_deadline = project.end_date.strftime("%d.%m.%Y") if project.end_date else None

        tasks_data = []
        for t in tasks:
            is_late = bool(
                t.deadline and t.deadline < now
                and not (t.current_step and t.current_step.is_last)
            )
            tasks_data.append(TaskSummaryResponse(
                task_id=t.task_id,
                name=t.name,
                description=t.description,
                priority=t.priority.value if t.priority else None,
                status=t.current_step.status_name if t.current_step else None,
                is_completed=t.current_step.is_last if t.current_step else False,
                is_late=is_late,
                deadline=t.deadline.strftime("%d.%m.%Y") if t.deadline else None,
                assigned_user=(
                    f"{t.assigned_user.name} {t.assigned_user.last_name}"
                    if t.assigned_user else None
                ),
                assigned_user_id=t.assigned_user_id,
                subtasks=[
                    SubtaskSummaryResponse(
                        subtask_id=s.subtask_id,
                        name=s.name,
                        description=s.description,
                        status=s.current_status.value if s.current_status else None,
                        deadline=s.deadline.strftime("%d.%m.%Y") if s.deadline else None,
                        assigned_user=(
                            f"{s.assigned_user.name} {s.assigned_user.last_name}"
                            if s.assigned_user else None
                        ),
                    )
                    for s in t.subtasks
                ],
                resources=[
                    TaskResourceSummaryResponse(
                        resource_id=tr.resource_id,
                        name=tr.resource.name if tr.resource else tr.resource_id,
                        resource_type=tr.resource.resource_type if tr.resource else None,
                        quantity=tr.quantity,
                        status=tr.status.value if tr.status else None,
                    )
                    for tr in t.resources
                ],
            ))

        members_data = [
            MemberResponse(
                user_id=w.user_id,
                name=w.user.name if w.user else "",
                last_name=w.user.last_name if w.user else "",
                role=w.role.name if w.role else None,
            )
            for w in project.works
            if w.user
        ]

        return ProjectDetailResponse(
            project_id=project.project_id,
            name=project.name,
            description=project.description,
            status=project.status.value if project.status else None,
            start_date=project.start_date.strftime("%d.%m.%Y") if project.start_date else None,
            end_date=project_deadline,
            is_manager=self._is_manager(project, current_user_id),
            stats=ProjectStatsResponse(
                total=total,
                completed=completed,
                late=late,
                progress=progress,
                deadline=project_deadline,
            ),
            members=members_data,
            tasks=tasks_data,
        )

    async def update_project(self, project_id: int, request, user_id: int):
        await self.ensure_user_is_admin(user_id)

        project = await self.project_repository.get_project_by_id(project_id)

        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        project.name = request.name
        project.description = request.description

        return await self.project_repository.update_project(project)