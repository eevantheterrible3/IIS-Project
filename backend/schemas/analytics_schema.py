from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class UsageSummary(BaseModel):
    total_generations: int
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int
    estimated_cost: float
    avg_latency_ms: float
    unique_documents: int


class TimeSeriesPoint(BaseModel):
    date: str
    generations: int
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int
    estimated_cost: float


class BreakdownItem(BaseModel):
    label: str
    generations: int
    total_tokens: int
    estimated_cost: float


class RecentGeneration(BaseModel):
    llm_usage_log_id: str
    created_at: Optional[datetime] = None
    generation_type: str
    model: Optional[str] = None
    document_name: Optional[str] = None
    document_type_name: Optional[str] = None
    user_name: Optional[str] = None
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: Optional[float] = None
    latency_ms: Optional[int] = None


class DashboardResponse(BaseModel):
    summary: UsageSummary
    time_series: List[TimeSeriesPoint]
    by_document_type: List[BreakdownItem]
    by_model: List[BreakdownItem]
    by_user: List[BreakdownItem]
    recent: List[RecentGeneration]
