from datetime import datetime

from fastapi import HTTPException

from models.resource import Resource
from schemas.resource_schema import CreateResourceRequest, UpdateResourceRequest, ResourceResponse


class ResourceService:
    def __init__(self, repository, task_resource_repository=None):
        self.repository = repository
        self.task_resource_repository = task_resource_repository

    async def get_all(self) -> list[ResourceResponse]:
        resources = await self.repository.get_all()
        return [ResourceResponse.model_validate(r) for r in resources]

    async def get_by_id(self, resource_id: str) -> ResourceResponse:
        resource = await self.repository.get_by_id(resource_id)
        if resource is None:
            raise HTTPException(status_code=404, detail="Resource not found")
        return ResourceResponse.model_validate(resource)

    async def create(self, data: CreateResourceRequest) -> ResourceResponse:
        resource = Resource(
            name=data.name,
            resource_type=data.resource_type,
            description=data.description,
            total_quantity=data.total_quantity
        )
        result = await self.repository.create(resource)
        return ResourceResponse.model_validate(result)

    async def update(self, resource_id: int, data: UpdateResourceRequest) -> ResourceResponse:
        resource = await self.repository.get_by_id(resource_id)
        if resource is None:
            raise HTTPException(status_code=404, detail="Resource not found")
        if data.name is not None:
            resource.name = data.name
        if data.resource_type is not None:
            resource.resource_type = data.resource_type
        if data.description is not None:
            resource.description = data.description
        if data.status is not None:
            resource.status = data.status
        if data.total_quantity is not None:
            resource.total_quantity = data.total_quantity
        result = await self.repository.update(resource)
        return ResourceResponse.model_validate(result)

    async def delete(self, resource_id: str):
        resource = await self.repository.get_by_id(resource_id)
        if resource is None:
            raise HTTPException(status_code=404, detail="Resource not found")
        if self.task_resource_repository is not None:
            in_use = await self.task_resource_repository.get_by_resource(resource_id)
            if in_use:
                raise HTTPException(
                    status_code=400,
                    detail="This resource is assigned to one or more tasks and cannot be deleted."
                )
        await self.repository.delete(resource)
        return {"message": "Resource deleted"}
