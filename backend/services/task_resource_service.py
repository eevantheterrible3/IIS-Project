from datetime import datetime

from fastapi import HTTPException

from models.task_resource import TaskResource, TaskResourceStatus
from schemas.task_resource_schema import CreateTaskResourceRequest, UpdateTaskResourceRequest, TaskResourceResponse


class TaskResourceService:
    def __init__(self, repository, resource_repository=None):
        self.repository = repository
        self.resource_repository = resource_repository

    async def get_by_task(self, task_id: str) -> list[TaskResourceResponse]:
        task_resources = await self.repository.get_by_task(task_id)
        return [TaskResourceResponse.model_validate(tr) for tr in task_resources]

    async def create(self, data: CreateTaskResourceRequest) -> TaskResourceResponse:
        existing = await self.repository.get_by_ids(data.task_id, data.resource_id)
        if existing is not None:
            raise HTTPException(status_code=400, detail="Resource already assigned to this task")
        task_resource = TaskResource(
            task_id=data.task_id,
            resource_id=data.resource_id,
            quantity=data.quantity,
            reserved_from=data.reserved_from,
            reserved_until=data.reserved_until
        )
        result = await self.repository.create(task_resource)
        return TaskResourceResponse.model_validate(result)

    async def update(self, task_id: int, resource_id: int, data: UpdateTaskResourceRequest) -> TaskResourceResponse:
        task_resource = await self.repository.get_by_ids(task_id, resource_id)
        if task_resource is None:
            raise HTTPException(status_code=404, detail="Task resource not found")
        if data.quantity is not None:
            task_resource.quantity = data.quantity
        if data.reserved_from is not None:
            task_resource.reserved_from = data.reserved_from
        if data.reserved_until is not None:
            task_resource.reserved_until = data.reserved_until
        if data.status is not None:
            task_resource.status = data.status
        result = await self.repository.update(task_resource)
        return TaskResourceResponse.model_validate(result)

    async def delete(self, task_id: int, resource_id: str):
        task_resource = await self.repository.get_by_ids(task_id, resource_id)
        if task_resource is None:
            raise HTTPException(status_code=404, detail="Task resource not found")
        await self.repository.delete(task_resource)
        return {"message": "Resource removed from task"}

    async def get_available_quantity(self, resource_id: str, reserved_from: str, reserved_until: str) -> dict:
        resource = await self.resource_repository.get_by_id(resource_id)
        if resource is None:
            raise HTTPException(status_code=404, detail="Resource not found")
        from_dt = datetime.strptime(reserved_from, "%Y-%m-%d")
        until_dt = datetime.strptime(reserved_until, "%Y-%m-%d")
        existing = await self.repository.get_by_resource_and_period(resource_id, from_dt, until_dt)
        already_reserved = sum(r.quantity for r in existing)
        return {"available": resource.total_quantity - already_reserved}

    async def create_for_task(self, task_id: str, resource_id: str, quantity: int, reserved_from: str, reserved_until: str):
        from_dt = datetime.strptime(reserved_from, "%Y-%m-%d") if reserved_from else None
        until_dt = datetime.strptime(reserved_until, "%Y-%m-%d") if reserved_until else None

        if from_dt and until_dt:
            result = await self.get_available_quantity(resource_id, reserved_from, reserved_until)
            if quantity > result["available"]:
                resource = await self.resource_repository.get_by_id(resource_id)
                raise HTTPException(
                    status_code=400,
                    detail=f"Not enough quantity for resource '{resource.name}'. "
                           f"Available: {result['available']}, requested: {quantity}."
                )

        task_resource = TaskResource(
            task_id=task_id,
            resource_id=resource_id,
            quantity=quantity,
            reserved_from=from_dt,
            reserved_until=until_dt,
            status=TaskResourceStatus.reserved,
        )
        return await self.repository.create(task_resource)
