from fastapi import HTTPException
from models.workflow_instance import WorkflowInstance
from schemas.workflow_instance_schema import (
    WorkflowInstanceCreateRequest,
    WorkflowInstanceUpdateRequest,
    WorkflowInstanceResponse,
)


class WorkflowInstanceService:
    def __init__(self, repository):
        self.repository = repository

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
        instance = WorkflowInstance(
            workflow_id=request.workflow_id,
            document_id=request.document_id,
            designated_user_id=request.designated_user_id,
            note=request.note,
        )
        created = await self.repository.create(instance)
        result = await self.repository.get_by_id(created.instance_id)
        return self._to_response(result)

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
        return WorkflowInstanceResponse(
            instance_id=instance.instance_id,
            workflow_id=instance.workflow_id,
            workflow_name=instance.workflow.name if instance.workflow else None,
            document_id=instance.document_id,
            current_step_id=instance.current_step_id,
            current_step_name=instance.current_step.name if instance.current_step else None,
            designated_user_id=instance.designated_user_id,
            designated_user_name=f"{instance.designated_user.name} {instance.designated_user.last_name}" if instance.designated_user else None,
            note=instance.note,
            started_at=instance.started_at,
            completed_at=instance.completed_at,
        )
