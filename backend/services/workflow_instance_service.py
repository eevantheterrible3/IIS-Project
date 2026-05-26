from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models.document import Document
from models.workflow_instance import WorkflowInstance
from models.workflow_instance_step import WorkflowInstanceStep
from schemas.workflow_instance_schema import (
    WorkflowInstanceCreateRequest,
    WorkflowInstanceUpdateRequest,
    WorkflowInstanceResponse,
)


class WorkflowInstanceService:
    def __init__(self, repository, workflow_repo=None, wha_repo=None, db=None):
        self.repository = repository
        self.workflow_repo = workflow_repo
        self.wha_repo = wha_repo
        self.db = db

    async def get_all(self) -> list[WorkflowInstanceResponse]:
        instances = await self.repository.get_all()
        return [self._to_response(i) for i in instances]

    async def get_by_id(self, instance_id: str) -> WorkflowInstanceResponse:
        instance = await self.repository.get_by_id(instance_id)
        if instance is None:
            raise HTTPException(status_code=404, detail="Workflow instance not found")
        return self._to_response(instance)

    async def get_by_document(self, document_id: str) -> list[WorkflowInstanceResponse]:
        instances = await self.repository.get_by_document(document_id)
        return [self._to_response(i) for i in instances]

    async def create(self, request: WorkflowInstanceCreateRequest) -> WorkflowInstanceResponse:
        workflow = await self.workflow_repo.get_by_id(request.workflow_id)
        if workflow is None:
            raise HTTPException(status_code=404, detail="Workflow not found")

        result = await self.db.execute(
            select(Document)
            .where(Document.document_id == request.document_id)
            .options(selectinload(Document.document_type))
        )
        document = result.scalar_one_or_none()
        if document is None:
            raise HTTPException(status_code=404, detail="Document not found")

        if workflow.document_type_id and document.document_type_id:
            if workflow.document_type_id != document.document_type_id:
                raise HTTPException(
                    status_code=400,
                    detail="Document type does not match the workflow's document type",
                )

        wha_steps = await self.wha_repo.get_by_workflow(request.workflow_id)

        start_step = next((s for s in wha_steps if s.is_start_step), None)

        instance = WorkflowInstance(
            workflow_id=request.workflow_id,
            document_id=request.document_id,
            current_step_id=start_step.action_id if start_step else None,
            designated_user_id=request.designated_user_id,
            note=request.note,
        )
        self.db.add(instance)
        await self.db.flush()

        for step in wha_steps:
            instance_step = WorkflowInstanceStep(
                instance_id=instance.instance_id,
                action_id=step.action_id,
                status="pending",
                progress=0,
            )
            self.db.add(instance_step)

        await self.db.commit()

        loaded = await self.repository.get_by_id(instance.instance_id)
        return self._to_response(loaded)

    async def update(self, instance_id: str, request: WorkflowInstanceUpdateRequest) -> WorkflowInstanceResponse:
        instance = await self.repository.get_by_id(instance_id)
        if instance is None:
            raise HTTPException(status_code=404, detail="Workflow instance not found")
        if request.current_step_id is not None:
            instance.current_step_id = request.current_step_id
        if request.designated_user_id is not None:
            instance.designated_user_id = request.designated_user_id
        if request.note is not None:
            instance.note = request.note
        if request.completed_at is not None:
            instance.completed_at = request.completed_at
        updated = await self.repository.update(instance)
        return self._to_response(updated)

    async def delete(self, instance_id: str):
        instance = await self.repository.get_by_id(instance_id)
        if instance is None:
            raise HTTPException(status_code=404, detail="Workflow instance not found")
        await self.repository.delete(instance)
        return {"message": "Workflow instance deleted successfully"}

    def _to_response(self, instance: WorkflowInstance) -> WorkflowInstanceResponse:
        wf = instance.workflow
        return WorkflowInstanceResponse(
            instance_id=instance.instance_id,
            workflow_id=instance.workflow_id,
            workflow_name=wf.name if wf else None,
            document_type_name=wf.document_type.name if wf and wf.document_type else None,
            document_id=instance.document_id,
            document_name=instance.document.name if instance.document else None,
            current_step_id=instance.current_step_id,
            current_step_name=instance.current_step.name if instance.current_step else None,
            designated_user_id=instance.designated_user_id,
            designated_user_name=f"{instance.designated_user.name} {instance.designated_user.last_name}" if instance.designated_user else None,
            note=instance.note,
            started_at=instance.started_at,
            completed_at=instance.completed_at,
        )
