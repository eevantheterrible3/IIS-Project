from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.document_rating import DocumentRating


class DocumentRatingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_document(self, document_id: str):
        result = await self.db.execute(
            select(DocumentRating)
            .where(DocumentRating.document_id == document_id)
            .options(selectinload(DocumentRating.user))
            .order_by(DocumentRating.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_id(self, document_rating_id: str):
        result = await self.db.execute(
            select(DocumentRating)
            .where(DocumentRating.document_rating_id == document_rating_id)
            .options(selectinload(DocumentRating.user))
        )
        return result.scalar_one_or_none()

    async def create(self, rating: DocumentRating):
        self.db.add(rating)
        await self.db.commit()
        await self.db.refresh(rating)
        return rating

    async def update(self, rating: DocumentRating):
        await self.db.commit()
        await self.db.refresh(rating)
        return rating

    async def delete(self, rating: DocumentRating):
        await self.db.delete(rating)
        await self.db.commit()
