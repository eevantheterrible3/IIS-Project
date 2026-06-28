import uuid
from datetime import datetime

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.usage_report import UsageReport


class UsageReportRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate(self, start: datetime, end: datetime) -> str:
        """Invoke the PL/pgSQL procedure to build a persisted report.

        We pass a pre-generated id so we don't depend on reading the procedure's
        INOUT return value back through the driver."""
        report_id = str(uuid.uuid4())
        await self.db.execute(
            text("CALL generate_usage_report(:start, :end, :rid)"),
            {"start": start, "end": end, "rid": report_id},
        )
        await self.db.commit()
        return report_id

    async def list_reports(self):
        result = await self.db.execute(
            select(UsageReport).order_by(UsageReport.generated_at.desc())
        )
        return result.scalars().all()

    async def get_report(self, report_id: str):
        result = await self.db.execute(
            select(UsageReport)
            .where(UsageReport.report_id == report_id)
            .options(selectinload(UsageReport.items))
        )
        return result.scalar_one_or_none()
