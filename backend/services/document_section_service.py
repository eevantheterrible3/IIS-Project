from fastapi import HTTPException

from schemas.document_section_schema import DocumentSectionResponse, DocumentSectionUpdateRequest


class DocumentSectionService:
    def __init__(self, repository):
        self.repository = repository

    async def get_by_document(self, document_id: int):
        sections = await self.repository.get_by_document(document_id)
        return [self._to_response(s) for s in sections]

    async def update(self, document_section_id: int, request: DocumentSectionUpdateRequest):
        section = await self.repository.get_by_id(document_section_id)
        if section is None:
            raise HTTPException(status_code=404, detail="Document section not found")

        section.content = request.content
        updated = await self.repository.update(section)
        return self._to_response(updated)

    def _to_response(self, section) -> DocumentSectionResponse:
        return DocumentSectionResponse(
            document_section_id=section.document_section_id,
            document_id=section.document_id,
            section_template_id=section.section_template_id,
            section_name=section.section_template.name if section.section_template else None,
            content=section.content,
            order_index=section.order_index,
            created_at=section.created_at,
            updated_at=section.updated_at,
        )
