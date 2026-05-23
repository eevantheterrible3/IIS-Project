from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SectionTemplateInTypeResponse(BaseModel):
    section_template_id: int
    name: str
    content_structure: str | None = None
    system_prompt: str | None = None
    order_index: int

    class Config:
        from_attributes = True


class DocumentTypeCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    system_prompt: Optional[str] = None


class DocumentTypeUpdateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    system_prompt: Optional[str] = None


class DocumentTypeResponse(BaseModel):
    document_type_id: int
    name: str
    description: str | None = None
    system_prompt: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class DocumentTypeDetailResponse(DocumentTypeResponse):
    section_templates: list[SectionTemplateInTypeResponse] = []
