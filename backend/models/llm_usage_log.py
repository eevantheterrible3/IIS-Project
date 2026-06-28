import uuid
from sqlalchemy import Column, String, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base


class LLMUsageLog(Base):
    """One row per LLM call (generate or refine) for a document.

    Foreign keys use ON DELETE SET NULL and are nullable so that usage history
    survives even if the related document / user / document type is removed.
    No ORM relationships are declared on purpose; analytics queries join
    explicitly, which keeps this model self-contained.
    """

    __tablename__ = "llm_usage_logs"

    llm_usage_log_id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )
    document_id = Column(
        String(36),
        ForeignKey("documents.document_id", ondelete="SET NULL"),
        nullable=True,
    )
    user_id = Column(
        String(36),
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
    )
    document_type_id = Column(
        String(36),
        ForeignKey("document_types.document_type_id", ondelete="SET NULL"),
        nullable=True,
    )

    generation_type = Column(String(16), nullable=False)  # "generate" | "refine"
    model = Column(String(128))

    prompt_tokens = Column(Integer, nullable=False, default=0)
    completion_tokens = Column(Integer, nullable=False, default=0)
    total_tokens = Column(Integer, nullable=False, default=0)

    estimated_cost = Column(Numeric(12, 6), nullable=True)  # USD
    latency_ms = Column(Integer, nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)
