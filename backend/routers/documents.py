import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from io import BytesIO
from fastapi.responses import FileResponse, StreamingResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from tempfile import NamedTemporaryFile
from services.pdf_text_extractor import PdfTextExtractor
from services.ai_tag_service import AiTagService
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from core.dependencies import get_current_user
from database import get_db
from models.document_version import DocumentVersion
from models.user import User
from models.workflow import Workflow
from models.workflow_instance import WorkflowInstance
from models.workflow_instance_step import WorkflowInstanceStep
from repositories.document_repository import DocumentRepository
from repositories.document_section_repository import DocumentSectionRepository
from repositories.document_version_repository import DocumentVersionRepository
from repositories.section_template_repository import SectionTemplateRepository
from repositories.workflow_has_action_repository import WorkflowHasActionRepository
from schemas.all_document_schema import DocumentCreateRequest, DocumentListItemResponse
from schemas.document_detail_schema import DocumentDetailResponse
from schemas.document_section_schema import DocumentSectionResponse
from schemas.document_update_schema import UpdateDocumentRequest
from schemas.document_version_schema import DocumentSaveRequest, DocumentVersionResponse
from services.document_section_service import DocumentSectionService
from services.document_service import DocumentService
from repositories.activity_repository import ActivityRepository
from models.activity import ActivityType
from schemas.activity_schema import ActivityResponse
from services.permission_service import PermissionService
from repositories.permission_repository import PermissionRepository
from schemas.document_permission_schema import DocumentUserPermissionResponse


router = APIRouter(prefix="/documents", tags=["Documents"])


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
    section_templates = await SectionTemplateRepository(db).get_by_document_type(request.document_type_id)
    service = DocumentService(DocumentRepository(db))
    doc = await service.create_document(request, current_user.user_id, section_templates)

    if request.document_type_id:
        result = await db.execute(
            select(Workflow)
            .where(Workflow.document_type_id == request.document_type_id)
            .limit(1)
        )
        workflow = result.scalar_one_or_none()
        if workflow:
            wha_steps = await WorkflowHasActionRepository(db).get_by_workflow(workflow.workflow_id)
            start_step = next((s for s in wha_steps if s.is_start_step), None)

            instance = WorkflowInstance(
                workflow_id=workflow.workflow_id,
                document_id=doc.document_id,
                current_step_id=start_step.action_id if start_step else None,
                designated_user_id=current_user.user_id,
            )
            db.add(instance)
            await db.flush()

            for wha in wha_steps:
                is_start = start_step and wha.action_id == start_step.action_id
                instance_step = WorkflowInstanceStep(
                    instance_id=instance.instance_id,
                    action_id=wha.action_id,
                    status="in_progress" if is_start else "pending",
                    progress=0,
                )
                db.add(instance_step)

            await db.commit()

    return DocumentListItemResponse(
        document_id=doc.document_id,
        name=doc.name,
        user_prompt=doc.user_prompt,
        document_type_id=doc.document_type_id,
        document_type_name=None,
        status=doc.status,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )

@router.post("/upload", response_model=DocumentListItemResponse)
async def upload_document(
    project_id: str = Form(...),
    name: str = Form(...),
    metadata_json: str = Form("[]"),
    tags_json: str = Form("[]"),
    document_type_id: str | None = Form(None),
    user_prompt: str | None = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DocumentService(DocumentRepository(db))

    try:
        metadata = json.loads(metadata_json)
    except json.JSONDecodeError:
        metadata = []

    try:
        tags = json.loads(tags_json)
    except json.JSONDecodeError:
        tags = []

    if not isinstance(tags, list):
        tags = []

    return await service.upload_document(
        project_id=project_id,
        user_id=current_user.user_id,
        name=name,
        file=file,
        metadata=metadata,
        tags=tags,
        document_type_id=document_type_id,
        user_prompt=user_prompt,
    )

@router.post("/suggest-tags")
async def suggest_tags_for_uploaded_file(
    name: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    content = await file.read()

    with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(content)
        temp_file_path = temp_file.name

    extractor = PdfTextExtractor()

    try:
        document_text = extractor.extract_text(temp_file_path, max_chars=5000)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    finally:
        Path(temp_file_path).unlink(missing_ok=True)

    if not document_text:
        raise HTTPException(
            status_code=400,
            detail="No text could be extracted from this PDF. The document may be scanned."
        )

    ai_tag_service = AiTagService()

    try:
        tags = await ai_tag_service.suggest_tags(
            document_name=name,
            document_text=document_text,
        )
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="AI tag service is currently unavailable."
        )

    if not tags:
        raise HTTPException(
            status_code=502,
            detail="AI service did not return any tags."
        )

    return {
        "tags": tags
    }

@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document_details(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DocumentService(DocumentRepository(db))

    document = await service.get_document_details(document_id)

    activity_repository = ActivityRepository(db)
    await activity_repository.create_activity(
        document_id=document_id,
        user_id=current_user.user_id,
        activity_type=ActivityType.VIEW
    )

    await db.commit()

    return document

@router.get("/{document_id}/file")
async def get_document_file(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    document_repository = DocumentRepository(db)
    document = await document_repository.get_document_details(document_id)

    if document is None or document.file_path is None:
        raise HTTPException(status_code=404, detail="Document file not found")

    file_path = Path(document.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File does not exist")

    return FileResponse(path=file_path, media_type="application/pdf", headers={"Content-Disposition": "inline"})


@router.delete("/delete/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
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

    updated_document = await service.update_document_tags_and_metadata(
        document_id,
        request
    )

    activity_repository = ActivityRepository(db)
    await activity_repository.create_activity(
        document_id=document_id,
        user_id=current_user.user_id,
        activity_type=ActivityType.UPDATE
    )

    await db.commit()

    return updated_document
@router.get("/{document_id}/sections", response_model=List[DocumentSectionResponse])
async def get_document_sections(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DocumentSectionService(DocumentSectionRepository(db))
    return await service.get_by_document(document_id)


@router.post("/{document_id}/save")
async def save_document(
    document_id: str,
    request: DocumentSaveRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    section_repo = DocumentSectionRepository(db)
    for item in request.sections:
        section = await section_repo.get_by_id(item.document_section_id)
        if section:
            section.content = item.content
            await section_repo.update(section)

    all_sections = await section_repo.get_by_document(document_id)
    snapshot = json.dumps([
        {
            "section_name": s.section_template.name if s.section_template else f"Section {i + 1}",
            "content": s.content or "",
            "order_index": s.order_index,
        }
        for i, s in enumerate(all_sections)
    ])

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

    version_repo = DocumentVersionRepository(db)
    latest = await version_repo.get_latest_number(document_id)
    version = DocumentVersion(
        document_id=document_id,
        author_id=current_user.user_id,
        instance_step_id=current_step_id,
        version_number=latest + 1,
        full_content=snapshot,
        note=request.note,
    )
    created = await version_repo.create(version)
    return {"version_number": created.version_number}


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
            note=v.note,
            full_content=v.full_content,
            created_at=v.created_at,
            author_name=f"{v.author.name} {v.author.last_name}" if v.author else None,
            instance_step_id=v.instance_step_id,
            step_name=v.instance_step.action.name if v.instance_step and v.instance_step.action else None,
        )
        for v in versions
    ]
@router.get("/{document_id}/activities", response_model=list[ActivityResponse])
async def get_document_activities(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    activity_repository = ActivityRepository(db)
    return await activity_repository.get_document_activities(document_id)

@router.get("/{document_id}/activities/report")
async def get_document_activities_report(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    document_repository = DocumentRepository(db)
    document = await document_repository.get_document_details(document_id)

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    activity_repository = ActivityRepository(db)
    activities = await activity_repository.get_document_activities(document_id)

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4
    y = height - 50

    def write_line(text, font="Helvetica", size=11, gap=20):
        nonlocal y

        if y < 60:
            pdf.showPage()
            y = height - 50

        pdf.setFont(font, size)
        pdf.drawString(50, y, text)
        y -= gap

    write_line("Document Activity Report", "Helvetica-Bold", 18, 35)

    write_line(f"Document: {document.name}")
    write_line(f"Project: {document.project.name if document.project else ''}")
    write_line(f"Document ID: {document.document_id}", gap=30)

    write_line("Activities:", "Helvetica-Bold", 13, 25)

    if not activities:
        write_line("No activities recorded for this document.")
    else:
        for activity in activities:
            user_name = "Unknown user"

            if activity.user:
                user_name = f"{activity.user.name} {activity.user.last_name}".strip()

            activity_type = activity.type.value if hasattr(activity.type, "value") else str(activity.type)
            activity_date = activity.date.strftime("%d.%m.%Y. %H:%M") if activity.date else ""

            write_line(f"- {user_name} {activity_type} document on {activity_date}", gap=22)

    pdf.save()
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="document_activity_{document_id}.pdf"'
        }
    )
@router.get("/{document_id}/permissions", response_model=list[DocumentUserPermissionResponse])
async def get_document_permissions(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = PermissionService(
        document_repository=DocumentRepository(db),
        permission_repository=PermissionRepository(db)
    )

    return await service.get_document_permissions(
        document_id=document_id,
        current_user_id=current_user.user_id
    )
@router.delete("/{document_id}/permissions/{user_id}/{permission_name}")
async def remove_document_permission(
    document_id: str,
    user_id: str,
    permission_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = PermissionService(
        document_repository=DocumentRepository(db),
        permission_repository=PermissionRepository(db)
    )

    return await service.remove_document_permission(
        document_id=document_id,
        target_user_id=user_id,
        permission_name=permission_name,
        current_user_id=current_user.user_id
    )