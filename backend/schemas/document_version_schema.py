from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DocumentVersionResponse(BaseModel):
    document_version_id: str
    version_number: int
    file_name: str | None = None
    note: str | None = None
    created_at: datetime | None = None
    author_name: str | None = None
    instance_step_id: str | None = None
    step_name: str | None = None
