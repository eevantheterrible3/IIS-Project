from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from repositories.document_repository import DocumentRepository
from services.document_service import DocumentService
from schemas.document_detail_schema import DocumentDetailResponse

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document_details(
    document_id: int,
    db: AsyncSession = Depends(get_db)
):
    document_repository = DocumentRepository(db)
    document_service = DocumentService(document_repository)

    return await document_service.get_document_details(document_id)