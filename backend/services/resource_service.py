from fastapi import HTTPException

from models.resource import Resource
from schemas.resource_schema import CreateResourceRequest, UpdateResourceRequest, ResourceResponse


class ResourceService:
    def __init__(self, repository):
        self.repository = repository

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
        await self.repository.delete(resource)
        return {"message": "Resource deleted"}
