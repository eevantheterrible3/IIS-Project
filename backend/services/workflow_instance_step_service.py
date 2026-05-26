from fastapi import HTTPException
from models.workflow_instance_step import WorkflowInstanceStep
from schemas.workflow_instance_step_schema import (
    WorkflowInstanceStepCreateRequest,
    WorkflowInstanceStepUpdateRequest,
    WorkflowInstanceStepResponse,
)


class WorkflowInstanceStepService:
    def __init__(self, repository):
        self.repository = repository

    async def get_by_instance(self, instance_id: str) -> list[WorkflowInstanceStepResponse]:
        steps = await self.repository.get_by_instance(instance_id)
        return [self._to_response(s) for s in steps]

    async def get_by_id(self, instance_step_id: str) -> WorkflowInstanceStepResponse:
        step = await self.repository.get_by_id(instance_step_id)
        if step is None:
            raise HTTPException(status_code=404, detail="Workflow instance step not found")
        return self._to_response(step)

    async def create(self, request: WorkflowInstanceStepCreateRequest) -> WorkflowInstanceStepResponse:
        step = WorkflowInstanceStep(
            instance_id=request.instance_id,
            action_id=request.action_id,
            status=request.status,
            progress=request.progress,
            assigned_user_id=request.assigned_user_id,
            note=request.note,
        )
        created = await self.repository.create(step)
        result = await self.repository.get_by_id(created.instance_step_id)
        return self._to_response(result)

    async def update(self, instance_step_id: str, request: WorkflowInstanceStepUpdateRequest) -> WorkflowInstanceStepResponse:
        step = await self.repository.get_by_id(instance_step_id)
        if step is None:
            raise HTTPException(status_code=404, detail="Workflow instance step not found")
        if request.status is not None:
            step.status = request.status
        if request.progress is not None:
            step.progress = request.progress
        if request.assigned_user_id is not None:
            step.assigned_user_id = request.assigned_user_id
        if request.note is not None:
            step.note = request.note
        if request.started_at is not None:
            step.started_at = request.started_at
        if request.completed_at is not None:
            step.completed_at = request.completed_at
        updated = await self.repository.update(step)
        return self._to_response(updated)

    async def delete(self, instance_step_id: str):
        step = await self.repository.get_by_id(instance_step_id)
        if step is None:
            raise HTTPException(status_code=404, detail="Workflow instance step not found")
        await self.repository.delete(step)
        return {"message": "Workflow instance step deleted successfully"}

    def _to_response(self, step: WorkflowInstanceStep) -> WorkflowInstanceStepResponse:
        return WorkflowInstanceStepResponse(
            instance_step_id=step.instance_step_id,
            instance_id=step.instance_id,
            action_id=step.action_id,
            action_name=step.action.name if step.action else None,
            status=step.status,
            progress=step.progress,
            assigned_user_id=step.assigned_user_id,
            assigned_user_name=f"{step.assigned_user.name} {step.assigned_user.last_name}" if step.assigned_user else None,
            note=step.note,
            started_at=step.started_at,
            completed_at=step.completed_at,
            created_at=step.created_at,
            updated_at=step.updated_at,
        )
