from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from database import get_db
from models.user import User
from repositories.resource_repository import ResourceRepository
from repositories.task_resource_repository import TaskResourceRepository
from schemas.resource_schema import CreateResourceRequest, UpdateResourceRequest, ResourceResponse
from services.resource_service import ResourceService
from services.task_resource_service import TaskResourceService

router = APIRouter(prefix="/project-realization/resources", tags=["PR Resources"])


@router.get("", response_model=list[ResourceResponse])
async def get_resources(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResourceService(ResourceRepository(db))
    return await service.get_all()


@router.post("", response_model=ResourceResponse)
async def create_resource(
    data: CreateResourceRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResourceService(ResourceRepository(db))
    return await service.create(data)


@router.put("/{resource_id}", response_model=ResourceResponse)
async def update_resource(
    resource_id: str,
    data: UpdateResourceRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResourceService(ResourceRepository(db))
    return await service.update(resource_id, data)


@router.delete("/{resource_id}")
async def delete_resource(
    resource_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResourceService(ResourceRepository(db), TaskResourceRepository(db))
    return await service.delete(resource_id)


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
