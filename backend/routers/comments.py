from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import get_current_user
from database import get_db
from models.comment import Comment
from models.user import User
from repositories.comment_repository import CommentRepository
from schemas.comment_schema import CommentCreateRequest, CommentResponse

router = APIRouter(prefix="/comments", tags=["Comments"])


@router.get("/document/{document_id}", response_model=List[CommentResponse])
async def get_document_comments(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = CommentRepository(db)
    comments = await repo.get_by_document(document_id)
    return [
        CommentResponse(
            comment_id=c.comment_id,
            document_id=c.document_id,
            version_id=c.version_id,
            user_id=c.user_id,
            user_name=f"{c.user.name} {c.user.last_name}" if c.user else None,
            content=c.content,
            created_at=c.created_at,
        )
        for c in comments
    ]


@router.post("", response_model=CommentResponse)
async def create_comment(
    request: CommentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = CommentRepository(db)
    comment = Comment(
        document_id=request.document_id,
        version_id=request.version_id,
        user_id=current_user.user_id,
        content=request.content,
    )
    created = await repo.create(comment)
    return CommentResponse(
        comment_id=created.comment_id,
        document_id=created.document_id,
        version_id=created.version_id,
        user_id=created.user_id,
        user_name=f"{current_user.name} {current_user.last_name}",
        content=created.content,
        created_at=created.created_at,
    )


@router.delete("/{comment_id}")
async def delete_comment(
    comment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Comment).where(Comment.comment_id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    repo = CommentRepository(db)
    await repo.delete(comment)
    return {"message": "Comment deleted"}
