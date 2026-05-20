from schemas.project_schema import ProjectListResponse
from fastapi import HTTPException
from models.project import Project, ProjectStatus
from datetime import datetime

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

    async def update_project(self, project_id: int, request, user_id: int):
        await self.ensure_user_is_admin(user_id)

        project = await self.project_repository.get_project_by_id(project_id)

        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        project.name = request.name
        project.description = request.description

        return await self.project_repository.update_project(project)