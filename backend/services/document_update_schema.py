from pydantic import BaseModel


class UpdateDocumentTagRequest(BaseModel):
    name: str


class UpdateDocumentMetadataRequest(BaseModel):
    name: str
    value: str


class UpdateDocumentRequest(BaseModel):
    tags: list[UpdateDocumentTagRequest]
    metadata: list[UpdateDocumentMetadataRequest]