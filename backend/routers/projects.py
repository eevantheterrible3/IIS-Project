from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.dependencies import get_current_user
from database import get_db
from models.user import User
from models.work import Work
from repositories.document_repository import DocumentRepository
from repositories.project_repository import ProjectRepository
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


@router.get("/{project_id}/documents")
async def get_project_documents(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = DocumentRepository(db)
    documents = await repo.get_documents_by_project_id(project_id)
    return [
        {
            "document_id": doc.document_id,
            "name": doc.name,
            "status": doc.status,
            "user_id": doc.user_id,
        }
        for doc in documents
    ]


@router.get("/{project_id}/members")
async def get_project_members(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Work)
        .where(Work.project_id == project_id)
        .options(selectinload(Work.user), selectinload(Work.role))
    )
    works = result.scalars().all()
    return [
        {
            "user_id": w.user.user_id,
            "name": f"{w.user.name} {w.user.last_name}",
            "role": w.role.name,
        }
        for w in works
    ]


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
