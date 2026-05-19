from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from repositories.project_repository import ProjectRepository
from repositories.document_repository import DocumentRepository
from services.project_service import ProjectService
from services.document_service import DocumentService
from schemas.project_schema import ProjectListResponse
from schemas.all_document_schema import DocumentListResponse

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/my", response_model=List[ProjectListResponse])
async def get_my_projects(
    user_id: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    project_repository = ProjectRepository(db)
    project_service = ProjectService(project_repository)

    return await project_service.get_projects_for_user(user_id)


@router.get("/{project_id}/documents", response_model=List[DocumentListResponse])
async def get_project_documents(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    document_repository = DocumentRepository(db)
    document_service = DocumentService(document_repository)

    return await document_service.get_documents_for_project(project_id)