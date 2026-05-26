from fastapi import HTTPException
from models.workflow_has_action import WorkflowHasAction
from schemas.workflow_has_action_schema import (
    WorkflowHasActionCreateRequest,
    WorkflowHasActionUpdateRequest,
    WorkflowHasActionResponse,
)


class WorkflowHasActionService:
    def __init__(self, repository):
        self.repository = repository

    async def get_by_workflow(self, workflow_id: str) -> list[WorkflowHasActionResponse]:
        links = await self.repository.get_by_workflow(workflow_id)
        return [self._to_response(link) for link in links]

    async def get_by_id(self, workflow_id: str, action_id: str) -> WorkflowHasActionResponse:
        link = await self.repository.get_by_id(workflow_id, action_id)
        if link is None:
            raise HTTPException(status_code=404, detail="Workflow-action link not found")
        return self._to_response(link)

    async def create(self, request: WorkflowHasActionCreateRequest) -> WorkflowHasActionResponse:
        link = WorkflowHasAction(
            workflow_id=request.workflow_id,
            action_id=request.action_id,
            next_action=request.next_action,
            is_start_step=request.is_start_step,
            condition_id=request.condition_id,
        )
        created = await self.repository.create(link)
        result = await self.repository.get_by_id(created.workflow_id, created.action_id)
        return self._to_response(result)

    async def update(
        self, workflow_id: str, action_id: str, request: WorkflowHasActionUpdateRequest
    ) -> WorkflowHasActionResponse:
        link = await self.repository.get_by_id(workflow_id, action_id)
        if link is None:
            raise HTTPException(status_code=404, detail="Workflow-action link not found")
        if request.next_action is not None:
            link.next_action = request.next_action
        if request.is_start_step is not None:
            link.is_start_step = request.is_start_step
        if request.condition_id is not None:
            link.condition_id = request.condition_id
        updated = await self.repository.update(link)
        return self._to_response(updated)

    async def delete(self, workflow_id: str, action_id: str):
        link = await self.repository.get_by_id(workflow_id, action_id)
        if link is None:
            raise HTTPException(status_code=404, detail="Workflow-action link not found")
        await self.repository.delete(link)
        return {"message": "Workflow-action link deleted successfully"}

    def _to_response(self, link: WorkflowHasAction) -> WorkflowHasActionResponse:
        return WorkflowHasActionResponse(
            workflow_id=link.workflow_id,
            action_id=link.action_id,
            action_name=link.action.name if link.action else None,
            next_action=link.next_action,
            next_action_name=link.next_action_ref.name if link.next_action_ref else None,
            is_start_step=link.is_start_step,
            condition_id=link.condition_id,
        )
