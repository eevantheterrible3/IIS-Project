from fastapi import HTTPException
from pathlib import Path
from schemas.all_document_schema import DocumentListResponse
from schemas.document_detail_schema import (
    DocumentDetailResponse,
    DocumentMetadataResponse,
    DocumentTagResponse
)


class DocumentService:
    def __init__(self, document_repository):
        self.document_repository = document_repository

    async def get_documents_for_project(self, project_id: int) -> list[DocumentListResponse]:
        documents = await self.document_repository.get_documents_by_project_id(project_id)

        return [
            DocumentListResponse(
                document_id=document.document_id,
                name=document.name
            )
            for document in documents
        ]

    async def get_document_details(self, document_id: int) -> DocumentDetailResponse:
        document = await self.document_repository.get_document_details(document_id)

        if document is None:
            raise HTTPException(status_code=404, detail="Document not found")

        return DocumentDetailResponse(
            document_id=document.document_id,
            name=document.name,
            status=document.status,
            user_prompt=document.user_prompt,
            created_at=document.created_at,
            updated_at=document.updated_at,
            author=f"{document.user.name} {document.user.last_name}",
            project_name=document.project.name,
            tags=[
                DocumentTagResponse(name=tag.tag.name)
                for tag in document.tags
            ],
            metadata=[
                DocumentMetadataResponse(
                    name=item.name,
                    value=item.value
                )
                for item in document.metadata_items
            ]
        )
        
        
    async def delete_document(self, document_id: int):
        document = await self.document_repository.get_document_by_id(document_id)

        if document is None:
            raise HTTPException(status_code=404, detail="Document not found")

        file_path = document.file_path
        await self.document_repository.delete_document(document)
        if file_path:
            path = Path(file_path)

        if path.exists() and path.is_file():
            path.unlink()
        return {"message": "Document deleted successfully"}