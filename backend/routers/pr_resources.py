from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from database import get_db
from models.user import User
from repositories.resource_repository import ResourceRepository
from repositories.task_resource_repository import TaskResourceRepository
from services.resource_service import ResourceService
from services.task_resource_service import TaskResourceService

router = APIRouter(prefix="/project-realization/resources", tags=["PR Resources"])


@router.get("")
async def get_resources(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResourceService(ResourceRepository(db))
    return await service.get_all()


@router.get("/{resource_id}/available")
async def get_available_quantity(
    resource_id: str,
    reserved_from: str,
    reserved_until: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TaskResourceService(TaskResourceRepository(db), ResourceRepository(db))
    return await service.get_available_quantity(resource_id, reserved_from, reserved_until)
