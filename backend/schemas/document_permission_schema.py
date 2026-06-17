from pydantic import BaseModel



class AddDocumentPermissionsRequest(BaseModel):
    user_ids: list[str]
    permissions: list[str]

class DocumentUserPermissionResponse(BaseModel):
    user_id: str
    username: str | None = None
    full_name: str
    email: str | None = None

    role: str | None = None
    is_project_member: bool

    permissions: list[str]

    can_read: bool
    can_create: bool
    can_update: bool
    can_delete: bool