from fastapi import HTTPException

from repositories.document_repository import DocumentRepository
from repositories.permission_repository import PermissionRepository
from schemas.document_permission_schema import DocumentUserPermissionResponse


class PermissionService:
    def __init__(
        self,
        document_repository: DocumentRepository,
        permission_repository: PermissionRepository
    ):
        self.document_repository = document_repository
        self.permission_repository = permission_repository

    async def get_document_permissions(
        self,
        document_id: str,
        current_user_id: str
    ) -> list[DocumentUserPermissionResponse]:
        document = await self.document_repository.get_document_details(document_id)

        if document is None:
            raise HTTPException(status_code=404, detail="Document not found")

        await self._check_can_view_permissions(
            current_user_id=current_user_id,
            project_id=document.project_id
        )

        project_members = await self.permission_repository.get_project_members_with_roles(
            document.project_id
        )

        allowed_users = await self.permission_repository.get_document_allowed_users(
            document_id
        )

        users_map = self._build_users_map(
            project_members=project_members,
            allowed_users=allowed_users
        )

        response = [
            self._map_user_permissions(item)
            for item in users_map.values()
        ]

        response.sort(key=lambda item: item.full_name.lower())

        return response

    async def _check_can_view_permissions(
        self,
        current_user_id: str,
        project_id: str
    ):
        current_user_is_admin = await self.permission_repository.is_admin(
            current_user_id
        )

        current_user_project_role = await self.permission_repository.get_user_role_for_project(
            user_id=current_user_id,
            project_id=project_id
        )

        normalized_role = (
            current_user_project_role.upper().strip()
            if current_user_project_role
            else None
        )

        current_user_is_project_manager = normalized_role == "PROJECT_MANAGER"

        if not current_user_is_admin and not current_user_is_project_manager:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to view document permissions."
            )

    def _build_users_map(self, project_members, allowed_users):
        users_map = {}

        for work in project_members:
            if work.user is None:
                continue

            role_name = work.role.name if work.role else None

            users_map[work.user.user_id] = {
                "user": work.user,
                "role": role_name,
                "is_project_member": True,
                "permissions": set()
            }

        for allowed in allowed_users:
            if allowed.user is None or allowed.permission is None:
                continue

            if allowed.user.user_id not in users_map:
                users_map[allowed.user.user_id] = {
                    "user": allowed.user,
                    "role": None,
                    "is_project_member": False,
                    "permissions": set()
                }

            users_map[allowed.user.user_id]["permissions"].add(
                allowed.permission.name
            )

        return users_map

    def _map_user_permissions(self, item) -> DocumentUserPermissionResponse:
        user = item["user"]
        role = item["role"]
        is_project_member = item["is_project_member"]
        permissions = list(item["permissions"])

        normalized_role = role.upper().strip() if role else None

        normalized_permissions = {
            permission.lower().strip()
            for permission in permissions
        }

        is_admin_or_project_manager = normalized_role in [
            "ADMIN",
            "PROJECT_MANAGER"
        ]

        is_team_member = normalized_role == "TEAM_MEMBER"

        if is_admin_or_project_manager:
            return DocumentUserPermissionResponse(
                user_id=user.user_id,
                username=user.username,
                full_name=f"{user.name} {user.last_name}",
                email=user.email,
                role=role,
                is_project_member=is_project_member,
                permissions=["all"],
                can_read=True,
                can_create=True,
                can_update=True,
                can_delete=True,
            )

        can_read = (
            is_team_member
            or "read" in normalized_permissions
            or "view" in normalized_permissions
        )

        can_create = (
            "create" in normalized_permissions
            or "add" in normalized_permissions
        )

        can_update = (
            "update" in normalized_permissions
            or "edit" in normalized_permissions
        )

        can_delete = "delete" in normalized_permissions

        return DocumentUserPermissionResponse(
            user_id=user.user_id,
            username=user.username,
            full_name=f"{user.name} {user.last_name}",
            email=user.email,
            role=role,
            is_project_member=is_project_member,
            permissions=permissions,
            can_read=can_read,
            can_create=can_create,
            can_update=can_update,
            can_delete=can_delete,
        )