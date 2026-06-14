from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.document import Document
from models.document_rating import DocumentRating


class DocumentRatingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, rating: DocumentRating):
        self.db.add(rating)
        await self.db.commit()
        await self.db.refresh(rating)
        return rating

    async def get_by_document(self, document_id: str):
        result = await self.db.execute(
            select(DocumentRating)
            .where(DocumentRating.document_id == document_id)
            .options(selectinload(DocumentRating.user))
            .order_by(DocumentRating.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_document_type(self, document_type_id: str):
        result = await self.db.execute(
            select(DocumentRating)
            .join(Document, Document.document_id == DocumentRating.document_id)
            .where(Document.document_type_id == document_type_id)
            .options(
                selectinload(DocumentRating.user),
                selectinload(DocumentRating.document),
            )
            .order_by(DocumentRating.created_at.desc())
        )
        return result.scalars().all()
