from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from repositories.document_repository import DocumentRepository
from repositories.document_section_repository import DocumentSectionRepository
from services.document_service import DocumentService
from services.document_section_service import DocumentSectionService
from schemas.document_detail_schema import DocumentDetailResponse
from schemas.document_update_schema import UpdateDocumentRequest
from schemas.document_section_schema import DocumentSectionResponse

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document_details(
    document_id: int,
    db: AsyncSession = Depends(get_db)
):
    document_repository = DocumentRepository(db)
    document_service = DocumentService(document_repository)

    return await document_service.get_document_details(document_id)
@router.get("/{document_id}/file")
async def get_document_file(
    document_id: int,
    db: AsyncSession = Depends(get_db)
):
    document_repository = DocumentRepository(db)
    document = await document_repository.get_document_details(document_id)

    if document is None or document.file_path is None:
        raise HTTPException(status_code=404, detail="Document file not found")

    file_path = Path(document.file_path)

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File does not exist")

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "inline"
        }
    )

@router.delete("/delete/{document_id}")
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db)
):
    document_repository = DocumentRepository(db)
    document_service = DocumentService(document_repository)

    return await document_service.delete_document(document_id)

@router.put("/{document_id}/edit", response_model=DocumentDetailResponse)
async def update_document_tags_and_metadata(
    document_id: int,
    request: UpdateDocumentRequest,
    db: AsyncSession = Depends(get_db)
):
    document_repository = DocumentRepository(db)
    document_service = DocumentService(document_repository)

    return await document_service.update_document_tags_and_metadata(
        document_id,
        request
    )


@router.get("/{document_id}/sections", response_model=List[DocumentSectionResponse])
async def get_document_sections(document_id: int, db: AsyncSession = Depends(get_db)):
    service = DocumentSectionService(DocumentSectionRepository(db))
    return await service.get_by_document(document_id)