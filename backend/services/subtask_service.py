from fastapi import HTTPException

from models.subtask import Subtask
from schemas.subtask_schema import CreateSubtaskRequest, UpdateSubtaskRequest, SubtaskResponse


class SubtaskService:
    def __init__(self, repository):
        self.repository = repository

    async def get_by_task(self, task_id: int) -> list[SubtaskResponse]:
        subtasks = await self.repository.get_by_task(task_id)
        return [SubtaskResponse.model_validate(s) for s in subtasks]

    async def get_by_id(self, subtask_id: int) -> SubtaskResponse:
        subtask = await self.repository.get_by_id(subtask_id)
        if subtask is None:
            raise HTTPException(status_code=404, detail="Subtask not found")
        return SubtaskResponse.model_validate(subtask)

    async def create(self, data: CreateSubtaskRequest) -> SubtaskResponse:
        subtask = Subtask(
            task_id=data.task_id,
            name=data.name,
            description=data.description,
            deadline=data.deadline,
            assigned_user_id=data.assigned_user_id
        )
        result = await self.repository.create(subtask)
        return SubtaskResponse.model_validate(result)

    async def update(self, subtask_id: int, data: UpdateSubtaskRequest) -> SubtaskResponse:
        subtask = await self.repository.get_by_id(subtask_id)
        if subtask is None:
            raise HTTPException(status_code=404, detail="Subtask not found")
        if data.name is not None:
            subtask.name = data.name
        if data.description is not None:
            subtask.description = data.description
        if data.deadline is not None:
            subtask.deadline = data.deadline
        if data.current_status is not None:
            subtask.current_status = data.current_status
        if data.assigned_user_id is not None:
            subtask.assigned_user_id = data.assigned_user_id
        result = await self.repository.update(subtask)
        return SubtaskResponse.model_validate(result)

    async def delete(self, subtask_id: int):
        subtask = await self.repository.get_by_id(subtask_id)
        if subtask is None:
            raise HTTPException(status_code=404, detail="Subtask not found")
        await self.repository.delete(subtask)
        return {"message": "Subtask deleted"}
