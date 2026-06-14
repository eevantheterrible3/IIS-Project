from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DocumentSectionUpdateRequest(BaseModel):
    content: Optional[str] = None


class ConversationTurn(BaseModel):
    role: str
    text: Optional[str] = None


class RefineSectionsRequest(BaseModel):
    history: list[ConversationTurn] = []


class DocumentSectionResponse(BaseModel):
    document_section_id: str
    document_id: str
    section_template_id: str | None = None
    section_name: str | None = None
    content: str | None = None
    order_index: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
