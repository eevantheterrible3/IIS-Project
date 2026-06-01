from fastapi import HTTPException

from models.task_workflow import TaskWorkflow
from models.task_workflow_step import TaskWorkflowStep
from schemas.task_workflow_schema import CreateTaskWorkflowRequest, TaskWorkflowResponse


class TaskWorkflowService:
    def __init__(self, repository, step_repository):
        self.repository = repository
        self.step_repository = step_repository

    async def get_all(self) -> list[TaskWorkflowResponse]:
        workflows = await self.repository.get_all()
        return [TaskWorkflowResponse.model_validate(w) for w in workflows]

    async def get_by_id(self, workflow_id: str) -> TaskWorkflowResponse:
        workflow = await self.repository.get_by_id(workflow_id)
        if workflow is None:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return TaskWorkflowResponse.model_validate(workflow)

    async def create(self, data: CreateTaskWorkflowRequest) -> TaskWorkflowResponse:
        workflow = TaskWorkflow(name=data.name, created_by=data.created_by)
        await self.repository.create(workflow)

        created_steps = []
        for step_data in data.steps:
            step = TaskWorkflowStep(
                task_workflow_id=workflow.task_workflow_id,
                status_name=step_data.status_name,
                is_first=step_data.is_first,
                is_last=step_data.is_last
            )
            await self.step_repository.create_and_flush(step)
            created_steps.append(step)

        for i in range(len(created_steps) - 1):
            created_steps[i].next_step_id = created_steps[i + 1].step_id

        await self.step_repository.commit()

        workflow = await self.repository.get_by_id(workflow.task_workflow_id)
        return TaskWorkflowResponse.model_validate(workflow)

    async def update(self, workflow_id: int, name: str) -> TaskWorkflowResponse:
        workflow = await self.repository.get_by_id(workflow_id)
        if workflow is None:
            raise HTTPException(status_code=404, detail="Workflow not found")
        workflow.name = name
        result = await self.repository.update(workflow)
        return TaskWorkflowResponse.model_validate(result)

    async def delete(self, workflow_id: str):
        workflow = await self.repository.get_by_id(workflow_id)
        if workflow is None:
            raise HTTPException(status_code=404, detail="Workflow not found")
        await self.repository.delete(workflow)
        return {"message": "Workflow deleted"}
