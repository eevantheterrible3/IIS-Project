from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from repositories.subtask_repository import SubtaskRepository
from services.subtask_service import SubtaskService
from schemas.subtask_schema import CreateSubtaskRequest, UpdateSubtaskRequest, SubtaskResponse

router = APIRouter(prefix="/subtasks", tags=["Subtasks"])


@router.get("/", response_model=List[SubtaskResponse])
async def get_subtasks(task_id: int = Query(...), db: AsyncSession = Depends(get_db)):
    service = SubtaskService(SubtaskRepository(db))
    return await service.get_by_task(task_id)


@router.get("/{subtask_id}", response_model=SubtaskResponse)
async def get_subtask(subtask_id: int, db: AsyncSession = Depends(get_db)):
    service = SubtaskService(SubtaskRepository(db))
    return await service.get_by_id(subtask_id)


@router.post("/", response_model=SubtaskResponse)
async def create_subtask(data: CreateSubtaskRequest, db: AsyncSession = Depends(get_db)):
    service = SubtaskService(SubtaskRepository(db))
    return await service.create(data)


@router.put("/{subtask_id}", response_model=SubtaskResponse)
async def update_subtask(subtask_id: int, data: UpdateSubtaskRequest, db: AsyncSession = Depends(get_db)):
    service = SubtaskService(SubtaskRepository(db))
    return await service.update(subtask_id, data)


@router.delete("/{subtask_id}")
async def delete_subtask(subtask_id: int, db: AsyncSession = Depends(get_db)):
    service = SubtaskService(SubtaskRepository(db))
    return await service.delete(subtask_id)
