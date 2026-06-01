from fastapi import HTTPException

from models.task import Task
from schemas.task_schema import CreateTaskRequest, UpdateTaskRequest, TaskListResponse, TaskDetailResponse


class TaskService:
    def __init__(self, repository):
        self.repository = repository

    async def get_by_project(self, project_id: str) -> list[TaskListResponse]:
        tasks = await self.repository.get_by_project(project_id)
        return [TaskListResponse.model_validate(t) for t in tasks]

    async def get_by_id(self, task_id: str) -> TaskDetailResponse:
        task = await self.repository.get_by_id(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return TaskDetailResponse.model_validate(task)

    async def create(self, data: CreateTaskRequest) -> TaskDetailResponse:
        task = Task(
            name=data.name,
            description=data.description,
            priority=data.priority,
            task_workflow_id=data.task_workflow_id,
            deadline=data.deadline,
            assigned_user_id=data.assigned_user_id,
            project_id=data.project_id
        )
        result = await self.repository.create(task)
        return TaskDetailResponse.model_validate(result)

    async def update(self, task_id: int, data: UpdateTaskRequest) -> TaskDetailResponse:
        task = await self.repository.get_by_id(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        if data.name is not None:
            task.name = data.name
        if data.description is not None:
            task.description = data.description
        if data.priority is not None:
            task.priority = data.priority
        if data.deadline is not None:
            task.deadline = data.deadline
        if data.assigned_user_id is not None:
            task.assigned_user_id = data.assigned_user_id
        if data.current_step_id is not None:
            task.current_step_id = data.current_step_id
        result = await self.repository.update(task)
        return TaskDetailResponse.model_validate(result)

    async def delete(self, task_id: str):
        task = await self.repository.get_by_id(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        await self.repository.delete(task)
        return {"message": "Task deleted"}
