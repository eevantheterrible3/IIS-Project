from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SectionSaveItem(BaseModel):
    document_section_id: str
    content: Optional[str] = None


class DocumentSaveRequest(BaseModel):
    sections: list[SectionSaveItem]
    note: Optional[str] = None


class DocumentVersionResponse(BaseModel):
    document_version_id: str
    version_number: int
    note: str | None = None
    full_content: str | None = None
    created_at: datetime | None = None
    author_name: str | None = None
