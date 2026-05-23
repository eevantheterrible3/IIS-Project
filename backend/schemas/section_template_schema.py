from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SectionTemplateCreateRequest(BaseModel):
    name: str
    content_structure: Optional[str] = None
    system_prompt: Optional[str] = None
    order_index: int = 0


class SectionTemplateUpdateRequest(BaseModel):
    name: str
    content_structure: Optional[str] = None
    system_prompt: Optional[str] = None
    order_index: int = 0


class SectionTemplateResponse(BaseModel):
    section_template_id: str
    document_type_id: str | None = None
    name: str
    content_structure: str | None = None
    system_prompt: str | None = None
    order_index: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
