from fastapi import HTTPException

from models.work import Work


class WorkService:
    def __init__(self, work_repository, project_repository):
        self.work_repository = work_repository
        self.project_repository = project_repository

    def _is_manager(self, project, user_id: str) -> bool:
        return any(
            w.user_id == user_id and w.role and w.role.name == "PROJECT_MANAGER"
            for w in project.works
        )

    async def add_member(self, project_id: str, user_id: str, current_user_id: str):
        project = await self.project_repository.get_by_id_with_members(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if not self._is_manager(project, current_user_id):
            raise HTTPException(status_code=403, detail="Only the project manager can add members")
        if any(w.user_id == user_id for w in project.works):
            raise HTTPException(status_code=409, detail="User is already a member of this project")

        member_role = await self.work_repository.get_role_by_name("TEAM_MEMBER")
        if not member_role:
            raise HTTPException(status_code=500, detail="TEAM_MEMBER role not found")

        await self.work_repository.add(
            Work(user_id=user_id, project_id=project_id, role_id=member_role.role_id)
        )
        return {"detail": "Member added"}

    async def remove_member(self, project_id: str, user_id: str, current_user_id: str):
        project = await self.project_repository.get_by_id_with_members(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if not self._is_manager(project, current_user_id):
            raise HTTPException(status_code=403, detail="Only the project manager can remove members")

        work = next((w for w in project.works if w.user_id == user_id), None)
        if not work:
            raise HTTPException(status_code=404, detail="Member not found in this project")
        if work.role and work.role.name == "PROJECT_MANAGER":
            raise HTTPException(status_code=400, detail="Cannot remove the project manager")

        await self.work_repository.delete(work)
        return {"detail": "Member removed"}
