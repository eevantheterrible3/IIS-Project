from fastapi import HTTPException
from models.document_rating import DocumentRating
from schemas.document_rating_schema import (
    DocumentRatingCreateRequest,
    DocumentRatingUpdateRequest,
    DocumentRatingResponse,
)


class DocumentRatingService:
    def __init__(self, repository):
        self.repository = repository

    async def get_by_document(self, document_id: str) -> list[DocumentRatingResponse]:
        ratings = await self.repository.get_by_document(document_id)
        return [self._to_response(r) for r in ratings]

    async def get_by_id(self, document_rating_id: str) -> DocumentRatingResponse:
        rating = await self.repository.get_by_id(document_rating_id)
        if rating is None:
            raise HTTPException(status_code=404, detail="Rating not found")
        return self._to_response(rating)

    async def create(self, request: DocumentRatingCreateRequest, user_id: str) -> DocumentRatingResponse:
        rating = DocumentRating(
            document_id=request.document_id,
            user_id=user_id,
            score=request.score,
            comment=request.comment,
        )
        created = await self.repository.create(rating)
        result = await self.repository.get_by_id(created.document_rating_id)
        return self._to_response(result)

    async def update(self, document_rating_id: str, request: DocumentRatingUpdateRequest) -> DocumentRatingResponse:
        rating = await self.repository.get_by_id(document_rating_id)
        if rating is None:
            raise HTTPException(status_code=404, detail="Rating not found")
        if request.score is not None:
            rating.score = request.score
        if request.comment is not None:
            rating.comment = request.comment
        updated = await self.repository.update(rating)
        return self._to_response(updated)

    async def delete(self, document_rating_id: str):
        rating = await self.repository.get_by_id(document_rating_id)
        if rating is None:
            raise HTTPException(status_code=404, detail="Rating not found")
        await self.repository.delete(rating)
        return {"message": "Rating deleted successfully"}

    def _to_response(self, rating: DocumentRating) -> DocumentRatingResponse:
        return DocumentRatingResponse(
            document_rating_id=rating.document_rating_id,
            document_id=rating.document_id,
            user_id=rating.user_id,
            user_name=f"{rating.user.name} {rating.user.last_name}" if rating.user else None,
            score=rating.score,
            comment=rating.comment,
            created_at=rating.created_at,
            updated_at=rating.updated_at,
        )
