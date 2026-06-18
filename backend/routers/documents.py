import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from fastapi.responses import FileResponse
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.dependencies import get_current_user
from database import get_db
from models.document_version import DocumentVersion
from models.user import User
from models.workflow_instance import WorkflowInstance
from models.workflow_instance_step import WorkflowInstanceStep
from repositories.document_repository import DocumentRepository
from repositories.document_version_repository import DocumentVersionRepository
from schemas.all_document_schema import DocumentCreateRequest, DocumentListItemResponse
from schemas.document_detail_schema import DocumentDetailResponse
from schemas.document_update_schema import UpdateDocumentRequest
from schemas.document_version_schema import DocumentVersionResponse
from models.activity import Activity, ActivityType
from services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = Path("uploads/documents")
ALLOWED_EXTENSIONS = {".docx", ".xlsx"}


@router.get("/my", response_model=List[DocumentListItemResponse])
async def get_my_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DocumentService(DocumentRepository(db))
    return await service.get_documents_for_user(current_user.user_id)


@router.post("", response_model=DocumentListItemResponse)
async def create_document(
    request: DocumentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DocumentService(DocumentRepository(db))
    doc = await service.create_document(request, current_user.user_id)

    db.add(Activity(document_id=doc.document_id, user_id=current_user.user_id, type=ActivityType.CREATE))
    await db.commit()

    return DocumentListItemResponse(
        document_id=doc.document_id,
        name=doc.name,
        user_prompt=doc.user_prompt,
        document_type_id=doc.document_type_id,
        document_type_name=None,
        file_type=doc.file_type,
        status=doc.status,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document_details(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DocumentService(DocumentRepository(db))
    result = await service.get_document_details(document_id)

    db.add(Activity(document_id=document_id, user_id=current_user.user_id, type=ActivityType.VIEW))
    await db.commit()

    return result


@router.delete("/delete/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    db.add(Activity(document_id=document_id, user_id=current_user.user_id, type=ActivityType.DELETE))
    await db.flush()
    service = DocumentService(DocumentRepository(db))
    return await service.delete_document(document_id)


@router.put("/{document_id}/edit", response_model=DocumentDetailResponse)
async def update_document(
    document_id: str,
    request: UpdateDocumentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DocumentService(DocumentRepository(db))
    return await service.update_document_tags_and_metadata(document_id, request)


@router.post("/{document_id}/upload")
async def upload_version(
    document_id: str,
    file: UploadFile = File(...),
    note: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    doc_repo = DocumentRepository(db)
    document = await doc_repo.get_document_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.file_type and ext != f".{document.file_type}":
        raise HTTPException(status_code=400, detail=f"Document expects .{document.file_type} files")

    version_repo = DocumentVersionRepository(db)
    latest = await version_repo.get_latest_number(document_id)
    version_number = latest + 1

    doc_dir = UPLOAD_DIR / document_id
    doc_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"v{version_number}_{file.filename}"
    file_path = doc_dir / stored_name

    content = await file.read()
    file_path.write_bytes(content)

    current_step_id = None
    instance_result = await db.execute(
        select(WorkflowInstance)
        .where(WorkflowInstance.document_id == document_id, WorkflowInstance.completed_at.is_(None))
        .limit(1)
    )
    active_instance = instance_result.scalar_one_or_none()
    if active_instance:
        step_result = await db.execute(
            select(WorkflowInstanceStep)
            .where(
                WorkflowInstanceStep.instance_id == active_instance.instance_id,
                WorkflowInstanceStep.status == "in_progress",
            )
            .limit(1)
        )
        active_step = step_result.scalar_one_or_none()
        if active_step:
            current_step_id = active_step.instance_step_id

    version = DocumentVersion(
        document_id=document_id,
        author_id=current_user.user_id,
        instance_step_id=current_step_id,
        version_number=version_number,
        file_path=str(file_path),
        file_name=file.filename,
        note=note,
    )
    created = await version_repo.create(version)

    db.add(Activity(document_id=document_id, user_id=current_user.user_id, type=ActivityType.UPDATE))
    await db.commit()

    return {"version_number": created.version_number, "file_name": created.file_name}


@router.get("/{document_id}/versions", response_model=List[DocumentVersionResponse])
async def get_document_versions(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = DocumentVersionRepository(db)
    versions = await repo.get_by_document(document_id)
    return [
        DocumentVersionResponse(
            document_version_id=v.document_version_id,
            version_number=v.version_number,
            file_name=v.file_name,
            note=v.note,
            created_at=v.created_at,
            author_name=f"{v.author.name} {v.author.last_name}" if v.author else None,
            instance_step_id=v.instance_step_id,
            step_name=v.instance_step.action.name if v.instance_step and v.instance_step.action else None,
        )
        for v in versions
    ]


@router.get("/{document_id}/versions/{version_id}/download")
async def download_version(
    document_id: str,
    version_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = DocumentVersionRepository(db)
    version = await repo.get_by_id(version_id)
    if not version or version.document_id != document_id:
        raise HTTPException(status_code=404, detail="Version not found")
    if not version.file_path:
        raise HTTPException(status_code=404, detail="No file for this version")

    path = Path(version.file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(path=path, filename=version.file_name or path.name)


class StatusUpdateRequest(BaseModel):
    status: str


class AssignRequest(BaseModel):
    user_id: str


@router.put("/{document_id}/status")
async def update_document_status(
    document_id: str,
    request: StatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = DocumentRepository(db)
    document = await repo.get_document_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    document.status = request.status
    await db.commit()
    return {"message": "Status updated", "status": request.status}


@router.put("/{document_id}/assign")
async def assign_document(
    document_id: str,
    request: AssignRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = DocumentRepository(db)
    document = await repo.get_document_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    document.user_id = request.user_id
    await db.commit()
    return {"message": "Document assigned"}
