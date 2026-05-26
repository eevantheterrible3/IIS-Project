from fastapi import HTTPException
from models.workflow import Workflow
from schemas.workflow_schema import WorkflowCreateRequest, WorkflowUpdateRequest, WorkflowResponse


class WorkflowService:
    def __init__(self, repository):
        self.repository = repository

    async def get_all(self) -> list[WorkflowResponse]:
        workflows = await self.repository.get_all()
        return [self._to_response(w) for w in workflows]

    async def get_by_id(self, workflow_id: str) -> WorkflowResponse:
        workflow = await self.repository.get_by_id(workflow_id)
        if workflow is None:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return self._to_response(workflow)

    async def create(self, request: WorkflowCreateRequest, user_id: str) -> WorkflowResponse:
        workflow = Workflow(
            name=request.name,
            created_by=request.created_by or user_id,
        )
        created = await self.repository.create(workflow)
        result = await self.repository.get_by_id(created.workflow_id)
        return self._to_response(result)

    async def update(self, workflow_id: str, request: WorkflowUpdateRequest) -> WorkflowResponse:
        workflow = await self.repository.get_by_id(workflow_id)
        if workflow is None:
            raise HTTPException(status_code=404, detail="Workflow not found")
        if request.name is not None:
            workflow.name = request.name
        updated = await self.repository.update(workflow)
        return self._to_response(updated)

    async def delete(self, workflow_id: str):
        workflow = await self.repository.get_by_id(workflow_id)
        if workflow is None:
            raise HTTPException(status_code=404, detail="Workflow not found")
        await self.repository.delete(workflow)
        return {"message": "Workflow deleted successfully"}

    def _to_response(self, workflow: Workflow) -> WorkflowResponse:
        return WorkflowResponse(
            workflow_id=workflow.workflow_id,
            name=workflow.name,
            created_by=workflow.created_by,
            creator_name=f"{workflow.creator.name} {workflow.creator.last_name}" if workflow.creator else None,
            created_at=workflow.created_at,
        )
