from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from database import get_db
from models.user import User
from repositories.document_rating_repository import DocumentRatingRepository
from schemas.document_rating_schema import (
    DocumentRatingCreateRequest,
    DocumentRatingUpdateRequest,
    DocumentRatingResponse,
)
from services.document_rating_service import DocumentRatingService

router = APIRouter(prefix="/document-ratings", tags=["Document Ratings"])


@router.get("/document/{document_id}", response_model=List[DocumentRatingResponse])
async def get_ratings_for_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DocumentRatingService(DocumentRatingRepository(db))
    return await service.get_by_document(document_id)


@router.get("/{document_rating_id}", response_model=DocumentRatingResponse)
async def get_rating(
    document_rating_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DocumentRatingService(DocumentRatingRepository(db))
    return await service.get_by_id(document_rating_id)


@router.post("", response_model=DocumentRatingResponse)
async def create_rating(
    request: DocumentRatingCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DocumentRatingService(DocumentRatingRepository(db))
    return await service.create(request, current_user.user_id)


@router.put("/{document_rating_id}", response_model=DocumentRatingResponse)
async def update_rating(
    document_rating_id: str,
    request: DocumentRatingUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DocumentRatingService(DocumentRatingRepository(db))
    return await service.update(document_rating_id, request)


@router.delete("/{document_rating_id}")
async def delete_rating(
    document_rating_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = DocumentRatingService(DocumentRatingRepository(db))
    return await service.delete(document_rating_id)
