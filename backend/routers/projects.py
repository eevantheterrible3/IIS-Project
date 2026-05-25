from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from database import get_db
from models.user import User
from repositories.document_repository import DocumentRepository
from repositories.project_repository import ProjectRepository
from schemas.all_document_schema import DocumentListResponse
from schemas.project_schema import ProjectCreateRequest, ProjectListResponse, ProjectUpdateRequest
from services.document_service import DocumentService
from services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/my", response_model=List[ProjectListResponse])
async def get_my_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(ProjectRepository(db))
    return await service.get_projects_for_user(current_user.user_id)


@router.get("/{project_id}/documents", response_model=List[DocumentListResponse])
async def get_project_documents(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DocumentService(DocumentRepository(db))
    return await service.get_documents_for_project(project_id)


@router.post("")
async def create_project(
    request: ProjectCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(ProjectRepository(db))
    return await service.create_project(request, current_user.user_id)


@router.put("/{project_id}")
async def update_project(
    project_id: str,
    request: ProjectUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(ProjectRepository(db))
    return await service.update_project(project_id, request, current_user.user_id)


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(ProjectRepository(db))
    return await service.delete_project(project_id, current_user.user_id)
