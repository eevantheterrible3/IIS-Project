from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DocumentSectionUpdateRequest(BaseModel):
    content: Optional[str] = None


class DocumentSectionResponse(BaseModel):
    document_section_id: int
    document_id: int
    section_template_id: int | None = None
    section_name: str | None = None
    content: str | None = None
    order_index: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
