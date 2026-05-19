from schemas.project_schema import ProjectListResponse


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