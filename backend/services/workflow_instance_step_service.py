from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from models.workflow_instance_step import WorkflowInstanceStep
from schemas.workflow_instance_step_schema import (
    WorkflowInstanceStepCreateRequest,
    WorkflowInstanceStepUpdateRequest,
    WorkflowInstanceStepResponse,
)


class WorkflowInstanceStepService:
    def __init__(self, repository, instance_repository=None, workflow_has_action_repository=None, db=None):
        self.repository = repository
        self.instance_repository = instance_repository
        self.workflow_has_action_repository = workflow_has_action_repository
        self.db = db

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
            progress=100 if request.status == "completed" else request.progress,
            assigned_user_id=request.assigned_user_id,
            note=request.note,
        )
        created = await self.repository.create(step)
        result = await self.repository.get_by_id(created.instance_step_id)
        return self._to_response(result)

    async def update(self, instance_step_id: str, request: WorkflowInstanceStepUpdateRequest, author_id: str | None = None) -> WorkflowInstanceStepResponse:
        step = await self.repository.get_by_id(instance_step_id)
        if step is None:
            raise HTTPException(status_code=404, detail="Workflow instance step not found")
        if (self.instance.current_step == self.action):
            raise HTTPException(status_code=404, detail="You can only update the progress in current step.")
        old_status = step.status
        if request.status == "completed" and old_status != "completed":
            await self._check_role_condition(step, author_id)
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
        if step.status == "completed":
            step.progress = 100

        updated = await self.repository.update(step)

        if request.status == "completed" and old_status != "completed":
            await self._advance_next_step(updated)

        result = await self.repository.get_by_id(instance_step_id)
        return self._to_response(result)

    async def _check_role_condition(self, step: WorkflowInstanceStep, user_id: str | None):
        if not self.instance_repository or not self.workflow_has_action_repository or not self.db or not user_id:
            return

        instance = await self.instance_repository.get_by_id(step.instance_id)
        if not instance:
            return

        link = await self.workflow_has_action_repository.get_by_id(
            instance.workflow_id, step.action_id
        )
        if not link or not link.condition_id:
            return

        from models.condition import Condition
        result = await self.db.execute(
            select(Condition)
            .where(Condition.condition_id == link.condition_id)
            .options(selectinload(Condition.role))
        )
        condition = result.scalar_one_or_none()
        if not condition or not condition.role_id:
            return

        from models.document import Document
        doc_result = await self.db.execute(
            select(Document.project_id)
            .where(Document.document_id == instance.document_id)
        )
        project_id = doc_result.scalar_one_or_none()
        if not project_id:
            return

        from models.work import Work
        work_result = await self.db.execute(
            select(Work)
            .where(Work.user_id == user_id, Work.project_id == project_id)
        )
        work = work_result.scalar_one_or_none()

        if not work or work.role_id != condition.role_id:
            role_name = condition.role.name if condition.role else "required role"
            raise HTTPException(
                status_code=403,
                detail=f"Only users with the '{role_name}' role can complete this step"
            )

    async def _advance_next_step(self, completed_step: WorkflowInstanceStep) -> WorkflowInstanceStep | None:
        if not self.instance_repository or not self.workflow_has_action_repository:
            return None

        instance = await self.instance_repository.get_by_id(completed_step.instance_id)
        if not instance:
            return None

        link = await self.workflow_has_action_repository.get_by_id(
            instance.workflow_id, completed_step.action_id
        )
        if not link or not link.next_action:
            return None

        all_steps = await self.repository.get_by_instance(instance.instance_id)
        for step in all_steps:
            if step.action_id == link.next_action and step.status == "pending":
                step.status = "in_progress"
                await self.repository.update(step)
                return step
        return None

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
