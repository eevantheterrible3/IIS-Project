from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func
from models.allows import Allows
from models.permission import Permission
from models.work import Work
from models.role import Role
from models.allows import Allows
from sqlalchemy import select, func
from models.user import User
from models.permission import Permission
from models.allows import Allows

class PermissionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def is_admin(self, user_id: str) -> bool:
        result = await self.db.execute(
            select(Work)
            .join(Role, Work.role_id == Role.role_id)
            .where(
                Work.user_id == user_id,
                func.upper(Role.name) == "ADMIN"
            )
            .limit(1)
        )

        return result.scalar_one_or_none() is not None

    async def get_user_role_for_project(
        self,
        user_id: str,
        project_id: str
    ) -> str | None:
        result = await self.db.execute(
            select(Work)
            .options(selectinload(Work.role))
            .where(
                Work.user_id == user_id,
                Work.project_id == project_id
            )
        )

        work = result.scalar_one_or_none()

        if work is None or work.role is None:
            return None

        return work.role.name

    async def get_project_members_with_roles(self, project_id: str):
        result = await self.db.execute(
            select(Work)
            .options(
                selectinload(Work.user),
                selectinload(Work.role)
            )
            .where(Work.project_id == project_id)
        )

        return result.scalars().all()
    async def get_document_allowed_users(self, document_id: str):
        result = await self.db.execute(
            select(Allows)
            .options(
                selectinload(Allows.user),
                selectinload(Allows.permission)
            )
            .where(Allows.document_id == document_id)
        )

        return result.scalars().all()
    async def remove_document_permission(
        self,
        document_id: str,
        user_id: str,
        permission_name: str
   ) -> bool:
        result = await self.db.execute(
            select(Allows)
            .join(Permission, Allows.permission_id == Permission.permission_id)
            .where(
                Allows.document_id == document_id,
                Allows.user_id == user_id,
                func.lower(Permission.name) == permission_name.lower()
            )
        )

        allowed_permission = result.scalar_one_or_none()

        if allowed_permission is None:
            return False

        await self.db.delete(allowed_permission)
        await self.db.flush()

        return True

    async def get_users_by_ids(self, user_ids: list[str]):
        result = await self.db.execute(
            select(User).where(User.user_id.in_(user_ids))
        )

        return result.scalars().all()

    async def get_permissions_by_names(self, permission_names: list[str]):
        normalized_names = [
            permission_name.lower().strip()
            for permission_name in permission_names
        ]

        result = await self.db.execute(
            select(Permission)
            .where(func.lower(Permission.name).in_(normalized_names))
        )

        return result.scalars().all()


    async def allow_permission_exists(
        self,
        document_id: str,
        user_id: str,
        permission_id: str
    ) -> bool:
        result = await self.db.execute(
            select(Allows)
            .where(
                Allows.document_id == document_id,
                Allows.user_id == user_id,
                Allows.permission_id == permission_id
            )
        )

        return result.scalar_one_or_none() is not None


    async def add_document_permission(
        self,
        document_id: str,
        user_id: str,
        permission_id: str
    ):
        allowed_permission = Allows(
            document_id=document_id,
            user_id=user_id,
            permission_id=permission_id
        )

        self.db.add(allowed_permission)
        await self.db.flush()

        return allowed_permission