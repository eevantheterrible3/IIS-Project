from fastapi import HTTPException
from models.workflow_has_action import WorkflowHasAction
from schemas.workflow_has_action_schema import (
    UNSET,
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
        if request.is_start_step:
            links = await self.get_by_workflow(request.workflow_id)
            for link in links:
                if link.is_start_step:
                    raise HTTPException(status_code=404, detail="Workflow already has a start step")


        link = WorkflowHasAction(
            workflow_id=request.workflow_id,
            action_id=request.action_id,
            next_action=request.next_action,
            is_start_step=request.is_start_step,
            condition_id=request.condition_id,
        )
        created = await self.repository.create(link)
        await self._recompute_order(request.workflow_id)
        result = await self.repository.get_by_id(created.workflow_id, created.action_id)
        return self._to_response(result)

    async def update(
        self, workflow_id: str, action_id: str, request: WorkflowHasActionUpdateRequest
    ) -> WorkflowHasActionResponse:
        link = await self.repository.get_by_id(workflow_id, action_id)
        if link is None:
            raise HTTPException(status_code=404, detail="Workflow-action link not found")
        if request.next_action != UNSET:
            link.next_action = request.next_action
        if request.is_start_step is not None:
            link.is_start_step = request.is_start_step
        if request.condition_id != UNSET:
            link.condition_id = request.condition_id
        await self.repository.update(link)
        await self._recompute_order(workflow_id)
        result = await self.repository.get_by_id(workflow_id, action_id)
        return self._to_response(result)

    async def delete(self, workflow_id: str, action_id: str):
        link = await self.repository.get_by_id(workflow_id, action_id)
        if link is None:
            raise HTTPException(status_code=404, detail="Workflow-action link not found")
        predecessors = await self.repository.get_pointing_to(workflow_id, action_id)
        for pred in predecessors:
            pred.next_action = None
        await self.repository.delete(link)
        await self._recompute_order(workflow_id)
        return {"message": "Workflow-action link deleted successfully"}

    async def _recompute_order(self, workflow_id: str):
        steps = await self.repository.get_by_workflow(workflow_id)
        by_action = {s.action_id: s for s in steps}
        start = next((s for s in steps if s.is_start_step), None)
        order = {}
        current, i = start, 0
        while current and current.action_id not in order:
            order[current.action_id] = i
            i += 1
            current = by_action.get(current.next_action) if current.next_action else None
        for s in steps:
            if s.action_id not in order:
                order[s.action_id] = i
                i += 1
        for s in steps:
            s.step_order = order[s.action_id]
        await self.repository.update(steps[0]) if steps else None

    def _to_response(self, link: WorkflowHasAction) -> WorkflowHasActionResponse:
        return WorkflowHasActionResponse(
            workflow_id=link.workflow_id,
            action_id=link.action_id,
            action_name=link.action.name if link.action else None,
            next_action=link.next_action,
            next_action_name=link.next_action_ref.name if link.next_action_ref else None,
            is_start_step=link.is_start_step,
            condition_id=link.condition_id,
            step_order=link.step_order,
        )
