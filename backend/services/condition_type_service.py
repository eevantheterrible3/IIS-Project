from fastapi import HTTPException
from models.condition_type import ConditionType
from schemas.condition_type_schema import (
    ConditionTypeCreateRequest,
    ConditionTypeUpdateRequest,
    ConditionTypeResponse,
)


class ConditionTypeService:
    def __init__(self, repository):
        self.repository = repository

    async def get_all(self) -> list[ConditionTypeResponse]:
        types = await self.repository.get_all()
        return [self._to_response(t) for t in types]

    async def get_by_id(self, condition_type_id: str) -> ConditionTypeResponse:
        ct = await self.repository.get_by_id(condition_type_id)
        if ct is None:
            raise HTTPException(status_code=404, detail="Condition type not found")
        return self._to_response(ct)

    async def create(self, request: ConditionTypeCreateRequest) -> ConditionTypeResponse:
        ct = ConditionType(name=request.name)
        created = await self.repository.create(ct)
        return self._to_response(created)

    async def update(self, condition_type_id: str, request: ConditionTypeUpdateRequest) -> ConditionTypeResponse:
        ct = await self.repository.get_by_id(condition_type_id)
        if ct is None:
            raise HTTPException(status_code=404, detail="Condition type not found")
        if request.name is not None:
            ct.name = request.name
        updated = await self.repository.update(ct)
        return self._to_response(updated)

    async def delete(self, condition_type_id: str):
        ct = await self.repository.get_by_id(condition_type_id)
        if ct is None:
            raise HTTPException(status_code=404, detail="Condition type not found")
        await self.repository.delete(ct)
        return {"message": "Condition type deleted successfully"}

    def _to_response(self, ct: ConditionType) -> ConditionTypeResponse:
        return ConditionTypeResponse(
            condition_type_id=ct.condition_type_id,
            name=ct.name,
        )
