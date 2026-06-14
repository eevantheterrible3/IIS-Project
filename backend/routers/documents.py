import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from database import get_db
from models.document_rating import DocumentRating
from models.document_version import DocumentVersion
from models.user import User
from repositories.document_rating_repository import DocumentRatingRepository
from repositories.document_repository import DocumentRepository
from repositories.document_section_repository import DocumentSectionRepository
from repositories.document_type_repository import DocumentTypeRepository
from repositories.document_version_repository import DocumentVersionRepository
from repositories.section_template_repository import SectionTemplateRepository
from schemas.all_document_schema import DocumentCreateRequest, DocumentListItemResponse
from schemas.document_detail_schema import DocumentDetailResponse
from schemas.document_rating_schema import RatingCreateRequest, RatingResponse
from schemas.document_section_schema import DocumentSectionResponse, RefineSectionsRequest
from schemas.document_update_schema import UpdateDocumentRequest
from schemas.document_version_schema import DocumentSaveRequest, DocumentVersionResponse
from services.document_section_service import DocumentSectionService
from services.document_service import DocumentService

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


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document_details(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DocumentService(DocumentRepository(db))
    return await service.get_document_details(document_id)


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
    return await service.update_document_tags_and_metadata(document_id, request)


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

    version_repo = DocumentVersionRepository(db)
    latest = await version_repo.get_latest_number(document_id)
    version = DocumentVersion(
        document_id=document_id,
        author_id=current_user.user_id,
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
        )
        for v in versions
    ]


def _sections_response(sections) -> List[DocumentSectionResponse]:
    return [
        DocumentSectionResponse(
            document_section_id=s.document_section_id,
            document_id=s.document_id,
            section_template_id=s.section_template_id,
            section_name=s.section_template.name if s.section_template else f"Section {i + 1}",
            content=s.content,
            order_index=s.order_index,
            created_at=s.created_at,
            updated_at=s.updated_at,
        )
        for i, s in enumerate(sections)
    ]


def _build_ai_service():
    from services.ai_service import AIDocumentService
    try:
        return AIDocumentService()
    except ValueError as e:
        raise HTTPException(status_code=503, detail=str(e))


async def _apply_generated(section_repo, document_id: str, generated: dict):
    sections = await section_repo.get_by_document(document_id)
    for section in sections:
        if section.document_section_id in generated:
            section.content = generated[section.document_section_id]
            await section_repo.update(section)
    return await section_repo.get_by_document(document_id)


@router.post("/{document_id}/generate-sections", response_model=List[DocumentSectionResponse])
async def generate_document_sections(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    document = await DocumentRepository(db).get_document_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    section_repo = DocumentSectionRepository(db)
    sections = await section_repo.get_by_document(document_id)
    if not sections:
        return []

    doc_type = await DocumentTypeRepository(db).get_by_id(document.document_type_id)
    ai_service = _build_ai_service()

    generated = await ai_service.generate_document(
        sections=sections,
        user_prompt=document.user_prompt or "",
        document_type_system_prompt=doc_type.system_prompt if doc_type else None,
    )

    document.status = "draft"
    updated = await _apply_generated(section_repo, document_id, generated)
    return _sections_response(updated)


@router.post("/{document_id}/refine-sections", response_model=List[DocumentSectionResponse])
async def refine_document_sections(
    document_id: str,
    request: RefineSectionsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    document = await DocumentRepository(db).get_document_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    section_repo = DocumentSectionRepository(db)
    sections = await section_repo.get_by_document(document_id)
    if not sections:
        return []

    doc_type = await DocumentTypeRepository(db).get_by_id(document.document_type_id)
    ai_service = _build_ai_service()

    generated = await ai_service.refine_document(
        sections=sections,
        conversation=[turn.model_dump() for turn in request.history],
        document_type_system_prompt=doc_type.system_prompt if doc_type else None,
    )

    updated = await _apply_generated(section_repo, document_id, generated)
    return _sections_response(updated)


@router.post("/{document_id}/accept")
async def accept_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    document = await DocumentRepository(db).get_document_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    section_repo = DocumentSectionRepository(db)
    all_sections = await section_repo.get_by_document(document_id)
    snapshot = json.dumps([
        {
            "section_name": s.section_template.name if s.section_template else f"Section {i + 1}",
            "content": s.content or "",
            "order_index": s.order_index,
        }
        for i, s in enumerate(all_sections)
    ])

    version_repo = DocumentVersionRepository(db)
    latest = await version_repo.get_latest_number(document_id)
    document.status = "active"
    version = DocumentVersion(
        document_id=document_id,
        author_id=current_user.user_id,
        version_number=latest + 1,
        full_content=snapshot,
        note="Accepted",
    )
    created = await version_repo.create(version)

    return {"version_number": created.version_number, "status": "active"}


@router.post("/{document_id}/revert/{version_id}", response_model=List[DocumentSectionResponse])
async def revert_document(
    document_id: str,
    version_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    versions = await DocumentVersionRepository(db).get_by_document(document_id)
    version = next((v for v in versions if v.document_version_id == version_id), None)
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    snapshot = json.loads(version.full_content or "[]")
    by_order = {item.get("order_index"): item.get("content", "") for item in snapshot}

    section_repo = DocumentSectionRepository(db)
    sections = await section_repo.get_by_document(document_id)
    for i, s in enumerate(sections):
        if s.order_index in by_order:
            s.content = by_order[s.order_index]
        elif i < len(snapshot):
            s.content = snapshot[i].get("content", "")
        await section_repo.update(s)

    updated = await section_repo.get_by_document(document_id)
    return _sections_response(updated)


@router.post("/{document_id}/reopen")
async def reopen_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    document = await DocumentRepository(db).get_document_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    document.status = "draft"
    await db.commit()
    return {"status": "draft"}


@router.post("/{document_id}/ratings", response_model=RatingResponse)
async def create_document_rating(
    document_id: str,
    request: RatingCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    document = await DocumentRepository(db).get_document_by_id(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    rating = DocumentRating(
        document_id=document_id,
        user_id=current_user.user_id,
        score=request.score,
        comment=request.comment,
    )
    created = await DocumentRatingRepository(db).create(rating)
    return RatingResponse(
        document_rating_id=created.document_rating_id,
        document_id=created.document_id,
        score=created.score,
        comment=created.comment,
        created_at=created.created_at,
        user_name=f"{current_user.name} {current_user.last_name}",
    )


@router.get("/{document_id}/ratings", response_model=List[RatingResponse])
async def get_document_ratings(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ratings = await DocumentRatingRepository(db).get_by_document(document_id)
    return [
        RatingResponse(
            document_rating_id=r.document_rating_id,
            document_id=r.document_id,
            score=r.score,
            comment=r.comment,
            created_at=r.created_at,
            user_name=f"{r.user.name} {r.user.last_name}" if r.user else None,
        )
        for r in ratings
    ]
