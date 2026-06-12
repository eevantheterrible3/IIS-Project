from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from database import get_db
from models.user import User
from repositories.task_workflow_repository import TaskWorkflowRepository
from services.task_workflow_service import TaskWorkflowService

router = APIRouter(prefix="/project-realization/workflows", tags=["PR Workflows"])


@router.get("")
async def get_workflows(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TaskWorkflowService(TaskWorkflowRepository(db), None)
    return await service.get_all_with_ordered_steps()
