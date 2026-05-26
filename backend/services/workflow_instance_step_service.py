import json

from fastapi import HTTPException
from models.document_version import DocumentVersion
from models.workflow_instance_step import WorkflowInstanceStep
from schemas.workflow_instance_step_schema import (
    WorkflowInstanceStepCreateRequest,
    WorkflowInstanceStepUpdateRequest,
    WorkflowInstanceStepResponse,
)


class WorkflowInstanceStepService:
    def __init__(self, repository, instance_repository=None, section_repository=None, version_repository=None, workflow_has_action_repository=None):
        self.repository = repository
        self.instance_repository = instance_repository
        self.section_repository = section_repository
        self.version_repository = version_repository
        self.workflow_has_action_repository = workflow_has_action_repository

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

    async def update(self, instance_step_id: str, request: WorkflowInstanceStepUpdateRequest, author_id: str | None = None) -> WorkflowInstanceStepResponse:
        step = await self.repository.get_by_id(instance_step_id)
        if step is None:
            raise HTTPException(status_code=404, detail="Workflow instance step not found")
        old_status = step.status
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
        if request.status == "completed" and old_status != "completed":
            step.progress = 100

        updated = await self.repository.update(step)

        if request.status == "completed" and old_status != "completed":
            next_step = await self._advance_next_step(updated)
            await self._create_version_snapshot(updated, author_id, next_step)

        return self._to_response(updated)

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

    async def _create_version_snapshot(self, completed_step: WorkflowInstanceStep, author_id: str | None, next_step: WorkflowInstanceStep | None):
        if not self.instance_repository or not self.section_repository or not self.version_repository:
            return

        instance = await self.instance_repository.get_by_id(completed_step.instance_id)
        if not instance:
            return

        sections = await self.section_repository.get_by_document(instance.document_id)
        snapshot = json.dumps([
            {
                "section_name": s.section_template.name if s.section_template else f"Section {i + 1}",
                "content": s.content or "",
                "order_index": s.order_index,
            }
            for i, s in enumerate(sections)
        ])

        latest = await self.version_repository.get_latest_number(instance.document_id)
        action_name = completed_step.action.name if completed_step.action else "Unknown"
        workflow_name = instance.workflow.name if instance.workflow else "Unknown"

        version = DocumentVersion(
            document_id=instance.document_id,
            author_id=author_id,
            instance_step_id=next_step.instance_step_id if next_step else None,
            version_number=latest + 1,
            full_content=snapshot,
            note=f'Auto-saved after completing step "{action_name}" in workflow "{workflow_name}"',
        )
        await self.version_repository.create(version)

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
