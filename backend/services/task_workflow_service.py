from fastapi import HTTPException

from models.task_workflow import TaskWorkflow
from models.task_workflow_step import TaskWorkflowStep
from schemas.task_workflow_schema import (
    CreateTaskWorkflowRequest,
    UpdateTaskWorkflowRequest,
    TaskWorkflowResponse,
    WorkflowStepOrderedResponse,
    WorkflowWithOrderedStepsResponse,
)


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

    async def create_for_pr(self, data, user_id: str) -> WorkflowWithOrderedStepsResponse:
        workflow = TaskWorkflow(name=data.name, created_by=user_id)
        await self.repository.create(workflow)

        created_steps = []
        for i, step_data in enumerate(data.steps):
            step = TaskWorkflowStep(
                task_workflow_id=workflow.task_workflow_id,
                status_name=step_data.status_name,
                is_first=(i == 0),
                is_last=(i == len(data.steps) - 1),
            )
            await self.step_repository.create_and_flush(step)
            created_steps.append(step)

        for i in range(len(created_steps) - 1):
            created_steps[i].next_step_id = created_steps[i + 1].step_id

        await self.step_repository.commit()

        workflow = await self.repository.get_by_id(workflow.task_workflow_id)
        return self._build_ordered_response(workflow)

    async def update_full(self, workflow_id: str, data: UpdateTaskWorkflowRequest) -> WorkflowWithOrderedStepsResponse:
        workflow = await self.repository.get_by_id(workflow_id)
        if workflow is None:
            raise HTTPException(status_code=404, detail="Workflow not found")

        workflow.name = data.name

        existing_steps = self._order_steps(workflow.steps)
        for i, step in enumerate(existing_steps):
            if i < len(data.steps):
                step.status_name = data.steps[i].status_name

        await self.step_repository.commit()

        workflow = await self.repository.get_by_id(workflow_id)
        return self._build_ordered_response(workflow)

    def _build_ordered_response(self, workflow: TaskWorkflow) -> WorkflowWithOrderedStepsResponse:
        steps = self._order_steps(workflow.steps)
        return WorkflowWithOrderedStepsResponse(
            task_workflow_id=workflow.task_workflow_id,
            name=workflow.name,
            steps=[
                WorkflowStepOrderedResponse(
                    step_id=s.step_id,
                    status_name=s.status_name,
                    is_first=s.is_first,
                    is_last=s.is_last,
                )
                for s in steps
            ],
        )

    def _order_steps(self, steps):
        if not steps:
            return []
        step_map = {s.step_id: s for s in steps}
        first = next((s for s in steps if s.is_first), steps[0])
        ordered, visited = [], set()
        current = first
        while current and current.step_id not in visited:
            ordered.append(current)
            visited.add(current.step_id)
            current = step_map.get(current.next_step_id)
        return ordered

    async def get_all_with_ordered_steps(self) -> list[WorkflowWithOrderedStepsResponse]:
        workflows = await self.repository.get_all()
        result = []
        for wf in workflows:
            steps = self._order_steps(wf.steps)
            result.append(WorkflowWithOrderedStepsResponse(
                task_workflow_id=wf.task_workflow_id,
                name=wf.name,
                steps=[
                    WorkflowStepOrderedResponse(
                        step_id=s.step_id,
                        status_name=s.status_name,
                        is_first=s.is_first,
                        is_last=s.is_last,
                    )
                    for s in steps
                ],
            ))
        return result
