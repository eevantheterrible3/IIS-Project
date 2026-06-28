import uuid
from sqlalchemy import (
    Column,
    String,
    Integer,
    BigInteger,
    Numeric,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class UsageReport(Base):
    """Header of a persisted LLM-usage report (one row per generated report).

    Populated by the PL/pgSQL procedure `generate_usage_report`."""

    __tablename__ = "usage_reports"

    report_id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )
    title = Column(String(255), nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    generated_at = Column(DateTime, server_default=func.now(), nullable=False)

    total_generations = Column(Integer, nullable=False, default=0)
    total_tokens = Column(BigInteger, nullable=False, default=0)
    total_cost = Column(Numeric(14, 6), nullable=True)

    items = relationship(
        "UsageReportItem",
        back_populates="report",
        cascade="all, delete-orphan",
    )


class UsageReportItem(Base):
    """One report line per document type (the GROUP BY result)."""

    __tablename__ = "usage_report_items"

    usage_report_item_id = Column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True
    )
    report_id = Column(
        String(36),
        ForeignKey("usage_reports.report_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    label = Column(String(255), nullable=False)  # document type name (or "Unknown")
    generations = Column(Integer, nullable=False, default=0)
    total_tokens = Column(BigInteger, nullable=False, default=0)
    estimated_cost = Column(Numeric(14, 6), nullable=True)

    report = relationship("UsageReport", back_populates="items")
