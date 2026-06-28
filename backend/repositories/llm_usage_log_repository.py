from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.document import Document
from models.document_type import DocumentType
from models.llm_usage_log import LLMUsageLog
from models.user import User


def _f(value) -> float:
    return float(value) if value is not None else 0.0


class LLMUsageLogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, log: LLMUsageLog) -> LLMUsageLog:
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    def _conditions(
        self,
        start: Optional[datetime],
        end: Optional[datetime],
        document_type_id: Optional[str],
        generation_type: Optional[str],
        user_id: Optional[str],
    ):
        conds = []
        if start is not None:
            conds.append(LLMUsageLog.created_at >= start)
        if end is not None:
            conds.append(LLMUsageLog.created_at <= end)
        if document_type_id:
            conds.append(LLMUsageLog.document_type_id == document_type_id)
        if generation_type:
            conds.append(LLMUsageLog.generation_type == generation_type)
        if user_id:
            conds.append(LLMUsageLog.user_id == user_id)
        return conds

    async def summary(self, **filters) -> dict:
        conds = self._conditions(**filters)
        stmt = select(
            func.count(LLMUsageLog.llm_usage_log_id).label("total_generations"),
            func.coalesce(func.sum(LLMUsageLog.total_tokens), 0).label("total_tokens"),
            func.coalesce(func.sum(LLMUsageLog.prompt_tokens), 0).label("prompt_tokens"),
            func.coalesce(func.sum(LLMUsageLog.completion_tokens), 0).label(
                "completion_tokens"
            ),
            func.coalesce(func.sum(LLMUsageLog.estimated_cost), 0).label(
                "estimated_cost"
            ),
            func.coalesce(func.avg(LLMUsageLog.latency_ms), 0).label("avg_latency_ms"),
            func.count(func.distinct(LLMUsageLog.document_id)).label(
                "unique_documents"
            ),
        ).where(*conds)
        row = (await self.db.execute(stmt)).one()
        return {
            "total_generations": int(row.total_generations or 0),
            "total_tokens": int(row.total_tokens or 0),
            "prompt_tokens": int(row.prompt_tokens or 0),
            "completion_tokens": int(row.completion_tokens or 0),
            "estimated_cost": _f(row.estimated_cost),
            "avg_latency_ms": _f(row.avg_latency_ms),
            "unique_documents": int(row.unique_documents or 0),
        }

    async def time_series(self, **filters) -> list:
        conds = self._conditions(**filters)
        day = func.date_trunc("day", LLMUsageLog.created_at).label("day")
        stmt = (
            select(
                day,
                func.count(LLMUsageLog.llm_usage_log_id).label("generations"),
                func.coalesce(func.sum(LLMUsageLog.total_tokens), 0).label(
                    "total_tokens"
                ),
                func.coalesce(func.sum(LLMUsageLog.prompt_tokens), 0).label(
                    "prompt_tokens"
                ),
                func.coalesce(func.sum(LLMUsageLog.completion_tokens), 0).label(
                    "completion_tokens"
                ),
                func.coalesce(func.sum(LLMUsageLog.estimated_cost), 0).label(
                    "estimated_cost"
                ),
            )
            .where(*conds)
            .group_by(day)
            .order_by(day)
        )
        rows = (await self.db.execute(stmt)).all()
        return [
            {
                "date": r.day.strftime("%Y-%m-%d") if r.day else "",
                "generations": int(r.generations or 0),
                "total_tokens": int(r.total_tokens or 0),
                "prompt_tokens": int(r.prompt_tokens or 0),
                "completion_tokens": int(r.completion_tokens or 0),
                "estimated_cost": _f(r.estimated_cost),
            }
            for r in rows
        ]

    async def _breakdown(self, label_col, join_model, join_on, **filters) -> list:
        conds = self._conditions(**filters)
        stmt = (
            select(
                label_col.label("label"),
                func.count(LLMUsageLog.llm_usage_log_id).label("generations"),
                func.coalesce(func.sum(LLMUsageLog.total_tokens), 0).label(
                    "total_tokens"
                ),
                func.coalesce(func.sum(LLMUsageLog.estimated_cost), 0).label(
                    "estimated_cost"
                ),
            )
            .select_from(LLMUsageLog)
            .where(*conds)
            .group_by(label_col)
            .order_by(func.coalesce(func.sum(LLMUsageLog.total_tokens), 0).desc())
        )
        if join_model is not None:
            stmt = stmt.join(join_model, join_on, isouter=True)
        rows = (await self.db.execute(stmt)).all()
        return [
            {
                # NULL joins (e.g. deleted user) yield "" via SQL concat — normalize to "Unknown"
                "label": (r.label or "").strip() or "Unknown",
                "generations": int(r.generations or 0),
                "total_tokens": int(r.total_tokens or 0),
                "estimated_cost": _f(r.estimated_cost),
            }
            for r in rows
        ]

    async def by_document_type(self, **filters) -> list:
        return await self._breakdown(
            DocumentType.name,
            DocumentType,
            DocumentType.document_type_id == LLMUsageLog.document_type_id,
            **filters,
        )

    async def by_model(self, **filters) -> list:
        return await self._breakdown(LLMUsageLog.model, None, None, **filters)

    async def by_user(self, **filters) -> list:
        return await self._breakdown(
            func.concat(User.name, " ", User.last_name),
            User,
            User.user_id == LLMUsageLog.user_id,
            **filters,
        )

    async def recent(self, limit: int = 20, **filters) -> list:
        conds = self._conditions(**filters)
        stmt = (
            select(
                LLMUsageLog.llm_usage_log_id,
                LLMUsageLog.created_at,
                LLMUsageLog.generation_type,
                LLMUsageLog.model,
                LLMUsageLog.prompt_tokens,
                LLMUsageLog.completion_tokens,
                LLMUsageLog.total_tokens,
                LLMUsageLog.estimated_cost,
                LLMUsageLog.latency_ms,
                Document.name.label("document_name"),
                DocumentType.name.label("document_type_name"),
                func.concat(User.name, " ", User.last_name).label("user_name"),
            )
            .select_from(LLMUsageLog)
            .join(Document, Document.document_id == LLMUsageLog.document_id, isouter=True)
            .join(
                DocumentType,
                DocumentType.document_type_id == LLMUsageLog.document_type_id,
                isouter=True,
            )
            .join(User, User.user_id == LLMUsageLog.user_id, isouter=True)
            .where(*conds)
            .order_by(LLMUsageLog.created_at.desc())
            .limit(limit)
        )
        rows = (await self.db.execute(stmt)).all()
        return [
            {
                "llm_usage_log_id": r.llm_usage_log_id,
                "created_at": r.created_at,
                "generation_type": r.generation_type,
                "model": r.model,
                "document_name": r.document_name,
                "document_type_name": r.document_type_name,
                "user_name": (r.user_name or "").strip() or None,
                "prompt_tokens": int(r.prompt_tokens or 0),
                "completion_tokens": int(r.completion_tokens or 0),
                "total_tokens": int(r.total_tokens or 0),
                "estimated_cost": _f(r.estimated_cost) if r.estimated_cost is not None else None,
                "latency_ms": r.latency_ms,
            }
            for r in rows
        ]
