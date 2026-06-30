from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import decode_token
from database import get_db
from models.user import User
from services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


async def _user_from_token(token: str, db: AsyncSession) -> User:
    exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise exc
        user_id = payload.get("sub")
        if not user_id:
            raise exc
    except JWTError:
        raise exc
    result = await db.execute(select(User).where(User.user_id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise exc
    return user


@router.get("/workflows")
async def workflow_report(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    await _user_from_token(token, db)
    service = ReportService(db)
    pdf_buffer = await service.generate_workflow_report()
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": 'inline; filename="workflow_report.pdf"'},
    )
