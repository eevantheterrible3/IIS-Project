from schemas.all_document_schema import DocumentListResponse


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