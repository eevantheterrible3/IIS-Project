from fastapi import HTTPException

from models.task_resource import TaskResource
from schemas.task_resource_schema import CreateTaskResourceRequest, UpdateTaskResourceRequest, TaskResourceResponse


class TaskResourceService:
    def __init__(self, repository):
        self.repository = repository

    async def get_by_task(self, task_id: int) -> list[TaskResourceResponse]:
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

    async def delete(self, task_id: int, resource_id: int):
        task_resource = await self.repository.get_by_ids(task_id, resource_id)
        if task_resource is None:
            raise HTTPException(status_code=404, detail="Task resource not found")
        await self.repository.delete(task_resource)
        return {"message": "Resource removed from task"}
