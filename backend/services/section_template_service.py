from fastapi import HTTPException

from models.section_template import SectionTemplate
from schemas.section_template_schema import SectionTemplateCreateRequest, SectionTemplateUpdateRequest


class SectionTemplateService:
    def __init__(self, repository):
        self.repository = repository

    async def get_by_document_type(self, document_type_id: int):
        return await self.repository.get_by_document_type(document_type_id)

    async def get_by_id(self, section_template_id: int):
        template = await self.repository.get_by_id(section_template_id)
        if template is None:
            raise HTTPException(status_code=404, detail="Section template not found")
        return template

    async def create(self, document_type_id: int, request: SectionTemplateCreateRequest):
        template = SectionTemplate(
            document_type_id=document_type_id,
            name=request.name,
            content_structure=request.content_structure,
            system_prompt=request.system_prompt,
            order_index=request.order_index,
        )
        return await self.repository.create(template)

    async def update(self, section_template_id: int, request: SectionTemplateUpdateRequest):
        template = await self.repository.get_by_id(section_template_id)
        if template is None:
            raise HTTPException(status_code=404, detail="Section template not found")

        template.name = request.name
        template.content_structure = request.content_structure
        template.system_prompt = request.system_prompt
        template.order_index = request.order_index

        return await self.repository.update(template)

    async def delete(self, section_template_id: int):
        template = await self.repository.get_by_id(section_template_id)
        if template is None:
            raise HTTPException(status_code=404, detail="Section template not found")

        await self.repository.delete(template)
        return {"message": "Section template deleted successfully"}
