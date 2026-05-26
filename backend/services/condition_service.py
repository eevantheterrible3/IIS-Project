from fastapi import HTTPException
from models.condition import Condition
from schemas.condition_schema import (
    ConditionCreateRequest,
    ConditionUpdateRequest,
    ConditionResponse,
)


class ConditionService:
    def __init__(self, repository):
        self.repository = repository

    async def get_all(self) -> list[ConditionResponse]:
        conditions = await self.repository.get_all()
        return [self._to_response(c) for c in conditions]

    async def get_by_id(self, condition_id: str) -> ConditionResponse:
        condition = await self.repository.get_by_id(condition_id)
        if condition is None:
            raise HTTPException(status_code=404, detail="Condition not found")
        return self._to_response(condition)

    async def create(self, request: ConditionCreateRequest) -> ConditionResponse:
        condition = Condition(
            condition_type_id=request.condition_type_id,
            document_type_id=request.document_type_id,
            role_id=request.role_id,
            description=request.description,
        )
        created = await self.repository.create(condition)
        result = await self.repository.get_by_id(created.condition_id)
        return self._to_response(result)

    async def update(self, condition_id: str, request: ConditionUpdateRequest) -> ConditionResponse:
        condition = await self.repository.get_by_id(condition_id)
        if condition is None:
            raise HTTPException(status_code=404, detail="Condition not found")
        if request.condition_type_id is not None:
            condition.condition_type_id = request.condition_type_id
        if request.document_type_id is not None:
            condition.document_type_id = request.document_type_id
        if request.role_id is not None:
            condition.role_id = request.role_id
        if request.description is not None:
            condition.description = request.description
        updated = await self.repository.update(condition)
        return self._to_response(updated)

    async def delete(self, condition_id: str):
        condition = await self.repository.get_by_id(condition_id)
        if condition is None:
            raise HTTPException(status_code=404, detail="Condition not found")
        await self.repository.delete(condition)
        return {"message": "Condition deleted successfully"}

    def _to_response(self, c: Condition) -> ConditionResponse:
        return ConditionResponse(
            condition_id=c.condition_id,
            condition_type_id=c.condition_type_id,
            condition_type_name=c.condition_type.name if c.condition_type else None,
            document_type_id=c.document_type_id,
            document_type_name=c.document_type.name if c.document_type else None,
            role_id=c.role_id,
            role_name=c.role.name if c.role else None,
            description=c.description,
        )
