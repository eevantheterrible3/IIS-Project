from fastapi import HTTPException
from models.workflow_action import WorkflowAction
from schemas.workflow_action_schema import (
    WorkflowActionCreateRequest,
    WorkflowActionUpdateRequest,
    WorkflowActionResponse,
)


class WorkflowActionService:
    def __init__(self, repository):
        self.repository = repository

    async def get_all(self) -> list[WorkflowActionResponse]:
        actions = await self.repository.get_all()
        return [self._to_response(a) for a in actions]

    async def get_by_id(self, action_id: str) -> WorkflowActionResponse:
        action = await self.repository.get_by_id(action_id)
        if action is None:
            raise HTTPException(status_code=404, detail="Workflow action not found")
        return self._to_response(action)

    async def create(self, request: WorkflowActionCreateRequest) -> WorkflowActionResponse:
        action = WorkflowAction(
            name=request.name,
            type=request.type,
            description=request.description,
        )
        created = await self.repository.create(action)
        return self._to_response(created)

    async def update(self, action_id: str, request: WorkflowActionUpdateRequest) -> WorkflowActionResponse:
        action = await self.repository.get_by_id(action_id)
        if action is None:
            raise HTTPException(status_code=404, detail="Workflow action not found")
        if request.name is not None:
            action.name = request.name
        if request.type is not None:
            action.type = request.type
        if request.description is not None:
            action.description = request.description
        updated = await self.repository.update(action)
        return self._to_response(updated)

    async def delete(self, action_id: str):
        action = await self.repository.get_by_id(action_id)
        if action is None:
            raise HTTPException(status_code=404, detail="Workflow action not found")
        await self.repository.delete(action)
        return {"message": "Workflow action deleted successfully"}

    def _to_response(self, action: WorkflowAction) -> WorkflowActionResponse:
        return WorkflowActionResponse(
            action_id=action.action_id,
            name=action.name,
            type=action.type,
            description=action.description,
        )
