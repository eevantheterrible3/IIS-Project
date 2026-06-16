import uuid
from fastapi import HTTPException
from pathlib import Path

from models.document import Document
from models.metadata import DocumentMetadata
from schemas.all_document_schema import (
    DocumentListResponse,
    ProjectDocumentListResponse,
    DocumentListItemResponse,
    DocumentCreateRequest
)
from schemas.document_detail_schema import (
    DocumentDetailResponse,
    DocumentMetadataResponse,
    DocumentTagResponse
)


class DocumentService:
    def __init__(self, document_repository):
        self.document_repository = document_repository

    async def get_documents_for_user(self, user_id: int) -> list[DocumentListItemResponse]:
        documents = await self.document_repository.get_by_user_id(user_id)
        return [
            DocumentListItemResponse(
                document_id=doc.document_id,
                name=doc.name,
                user_prompt=doc.user_prompt,
                document_type_id=doc.document_type_id,
                document_type_name=doc.document_type.name if doc.document_type else None,
                status=doc.status,
                created_at=doc.created_at,
                updated_at=doc.updated_at,
            )
            for doc in documents
        ]

    async def create_document(self, request: DocumentCreateRequest, user_id: int, section_templates: list):
        from models.document import Document
        document = Document(
            name=request.name,
            user_id=user_id,
            project_id=request.project_id,
            document_type_id=request.document_type_id,
            user_prompt=request.user_prompt,
            status="draft",
        )
        return await self.document_repository.create_document(document, section_templates)

    async def upload_document(
        self,
        project_id: str,
        user_id: str,
        name: str,
        file,
        metadata: list,
        document_type_id: str | None = None,
        user_prompt: str | None = None,
    ):
        upload_dir = Path("uploads/documents")
        upload_dir.mkdir(parents=True, exist_ok=True)

        original_filename = Path(file.filename).name
        stored_filename = f"{uuid.uuid4()}_{original_filename}"
        file_path = upload_dir / stored_filename

        content = await file.read()
        file_path.write_bytes(content)

        document = Document(
            name=name,
            user_id=user_id,
            project_id=project_id,
            document_type_id=document_type_id if document_type_id else None,
            user_prompt=user_prompt,
            file_path=str(file_path),
            status="draft",
        )

        metadata_items = []

        for item in metadata:
            metadata_name = item.get("name")
            metadata_value = item.get("value")

            if metadata_name and metadata_name.strip():
                metadata_items.append(
                    DocumentMetadata(
                        name=metadata_name.strip(),
                        value=metadata_value
                    )
                )

        uploaded_document = await self.document_repository.create_uploaded_document(
            document=document,
            metadata_items=metadata_items,
        )

        return DocumentListItemResponse(
            document_id=uploaded_document.document_id,
            name=uploaded_document.name,
            user_prompt=uploaded_document.user_prompt,
            document_type_id=uploaded_document.document_type_id,
            document_type_name=None,
            status=uploaded_document.status,
            created_at=uploaded_document.created_at,
            updated_at=uploaded_document.updated_at,
        )

    async def get_documents_for_project(
        self,
        project_id: str,
        name: str | None = None,
        author: str | None = None,
        date: str | None = None,
        document_type: str | None = None,
        tag: str | None = None,
    ) -> list[ProjectDocumentListResponse]:
        documents = await self.document_repository.get_documents_by_project_id(
            project_id,
            name=name,
            author=author,
            date=date,
            document_type=document_type,
            tag=tag,
        )

        return [
            ProjectDocumentListResponse(
                document_id=document.document_id,
                name=document.name,
                document_type_name=document.document_type.name if document.document_type else None,
                created_at=document.created_at,
                status=document.status,
                tags=[
                    item.tag.name
                    for item in document.tags
                    if item.tag is not None
                ],
                author=f"{document.user.name} {document.user.last_name}" if document.user else None,
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
            project_id=document.project.project_id,
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

    async def update_document_tags_and_metadata(self, document_id: int, request):
        document = await self.document_repository.get_document_details(document_id)

        if document is None:
            raise HTTPException(status_code=404, detail="Document not found")

        await self.document_repository.update_document_tags_and_metadata(
            document,
            request.tags,
            request.metadata
        )

        return await self.get_document_details(document_id)
