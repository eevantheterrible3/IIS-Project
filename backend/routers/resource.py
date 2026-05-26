from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from repositories.resource_repository import ResourceRepository
from services.resource_service import ResourceService
from schemas.resource_schema import CreateResourceRequest, UpdateResourceRequest, ResourceResponse

router = APIRouter(prefix="/resources", tags=["Resources"])


@router.get("/", response_model=List[ResourceResponse])
async def get_all_resources(db: AsyncSession = Depends(get_db)):
    service = ResourceService(ResourceRepository(db))
    return await service.get_all()


@router.post("/", response_model=ResourceResponse)
async def create_resource(data: CreateResourceRequest, db: AsyncSession = Depends(get_db)):
    service = ResourceService(ResourceRepository(db))
    return await service.create(data)


@router.put("/{resource_id}", response_model=ResourceResponse)
async def update_resource(resource_id: str, data: UpdateResourceRequest, db: AsyncSession = Depends(get_db)):
    service = ResourceService(ResourceRepository(db))
    return await service.update(resource_id, data)


@router.delete("/{resource_id}")
async def delete_resource(resource_id: str, db: AsyncSession = Depends(get_db)):
    service = ResourceService(ResourceRepository(db))
    return await service.delete(resource_id)
