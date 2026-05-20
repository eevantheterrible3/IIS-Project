from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.project import Project
from models.work import Work


class ProjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_works(self, user_id: int):
        result = await self.db.execute(
            select(Work)
            .where(Work.user_id == user_id)
            .options(
                selectinload(Work.project),
                selectinload(Work.role)
            )
        )
        return result.scalars().all()

    async def get_all_projects(self):
        result = await self.db.execute(select(Project))
        return result.scalars().all()

    async def get_project_by_id(self, project_id: int):
        result = await self.db.execute(
            select(Project).where(Project.project_id == project_id)
        )
        return result.scalar_one_or_none()

    async def delete_project(self, project: Project):
        await self.db.delete(project)
        await self.db.commit()