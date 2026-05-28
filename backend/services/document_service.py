from fastapi import HTTPException
from pathlib import Path
from schemas.all_document_schema import DocumentListResponse, DocumentListItemResponse, DocumentCreateRequest
from schemas.document_detail_schema import (
    DocumentDetailResponse,
    DocumentMetadataResponse,
    DocumentTagResponse
)


class DocumentService:
    def __init__(self, document_repository, workflow_repo=None, wha_repo=None, db=None):
        self.document_repository = document_repository
        self.workflow_repo = workflow_repo
        self.wha_repo = wha_repo
        self.db = db

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

    async def create_document(self, request: DocumentCreateRequest, user_id: str, section_templates: list):
        from models.document import Document
        from models.workflow import Workflow
        from models.workflow_instance import WorkflowInstance
        from models.workflow_instance_step import WorkflowInstanceStep
        from sqlalchemy import select

        document = Document(
            name=request.name,
            user_id=user_id,
            project_id=request.project_id,
            document_type_id=request.document_type_id,
            user_prompt=request.user_prompt,
            status="draft",
        )
        doc = await self.document_repository.create_document(document, section_templates)

        if request.document_type_id and self.wha_repo and self.db:
            result = await self.db.execute(
                select(Workflow)
                .where(Workflow.document_type_id == request.document_type_id)
                .limit(1)
            )
            workflow = result.scalar_one_or_none()
            if workflow:
                wha_steps = await self.wha_repo.get_by_workflow(workflow.workflow_id)
                start_step = next((s for s in wha_steps if s.is_start_step), None)

                instance = WorkflowInstance(
                    workflow_id=workflow.workflow_id,
                    document_id=doc.document_id,
                    current_step_id=start_step.action_id if start_step else None,
                    designated_user_id=user_id,
                )
                self.db.add(instance)
                await self.db.flush()

                for wha in wha_steps:
                    is_start = start_step and wha.action_id == start_step.action_id
                    instance_step = WorkflowInstanceStep(
                        instance_id=instance.instance_id,
                        action_id=wha.action_id,
                        status="in_progress" if is_start else "pending",
                        progress=0,
                    )
                    self.db.add(instance_step)

                await self.db.commit()

        return doc

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
