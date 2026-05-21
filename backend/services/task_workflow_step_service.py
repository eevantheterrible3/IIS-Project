from fastapi import HTTPException

from models.task_workflow_step import TaskWorkflowStep
from schemas.task_workflow_step_schema import CreateTaskWorkflowStepRequest, TaskWorkflowStepResponse


class TaskWorkflowStepService:
    def __init__(self, repository):
        self.repository = repository

    async def get_by_workflow(self, workflow_id: int) -> list[TaskWorkflowStepResponse]:
        steps = await self.repository.get_by_workflow(workflow_id)
        return [TaskWorkflowStepResponse.model_validate(s) for s in steps]

    async def get_by_id(self, step_id: int) -> TaskWorkflowStepResponse:
        step = await self.repository.get_by_id(step_id)
        if step is None:
            raise HTTPException(status_code=404, detail="Step not found")
        return TaskWorkflowStepResponse.model_validate(step)

    async def create(self, data: CreateTaskWorkflowStepRequest) -> TaskWorkflowStepResponse:
        step = TaskWorkflowStep(
            task_workflow_id=data.task_workflow_id,
            status_name=data.status_name,
            next_step_id=data.next_step_id,
            is_first=data.is_first,
            is_last=data.is_last
        )
        result = await self.repository.create(step)
        return TaskWorkflowStepResponse.model_validate(result)

    async def delete(self, step_id: int):
        step = await self.repository.get_by_id(step_id)
        if step is None:
            raise HTTPException(status_code=404, detail="Step not found")
        await self.repository.delete(step)
        return {"message": "Step deleted"}
