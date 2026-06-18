from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.comment import Comment


class CommentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_document(self, document_id: str):
        result = await self.db.execute(
            select(Comment)
            .where(Comment.document_id == document_id)
            .options(selectinload(Comment.user))
            .order_by(Comment.created_at.desc())
        )
        return result.scalars().all()

    async def create(self, comment: Comment):
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def delete(self, comment: Comment):
        await self.db.delete(comment)
        await self.db.commit()
