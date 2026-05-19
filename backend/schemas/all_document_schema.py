from pydantic import BaseModel


class DocumentListResponse(BaseModel):
    document_id: int
    name: str