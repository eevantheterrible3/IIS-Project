from fastapi import HTTPException

from models.document_type import DocumentType
from schemas.document_type_schema import DocumentTypeCreateRequest, DocumentTypeUpdateRequest


class DocumentTypeService:
    def __init__(self, repository):
        self.repository = repository

    async def get_all(self):
        return await self.repository.get_all()

    async def get_by_id(self, document_type_id: int):
        document_type = await self.repository.get_by_id(document_type_id)
        if document_type is None:
            raise HTTPException(status_code=404, detail="Document type not found")
        return document_type

    async def create(self, request: DocumentTypeCreateRequest):
        document_type = DocumentType(
            name=request.name,
            description=request.description,
            system_prompt=request.system_prompt,
        )
        return await self.repository.create(document_type)

    async def update(self, document_type_id: int, request: DocumentTypeUpdateRequest):
        document_type = await self.repository.get_by_id(document_type_id)
        if document_type is None:
            raise HTTPException(status_code=404, detail="Document type not found")

        document_type.name = request.name
        document_type.description = request.description
        document_type.system_prompt = request.system_prompt

        return await self.repository.update(document_type)

    async def delete(self, document_type_id: int):
        document_type = await self.repository.get_by_id(document_type_id)
        if document_type is None:
            raise HTTPException(status_code=404, detail="Document type not found")

        await self.repository.delete(document_type)
        return {"message": "Document type deleted successfully"}
