from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.document import Document
from models.is_marked import IsMarked
from models.tag import Tag
from models.metadata import DocumentMetadata

class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_documents_by_project_id(self, project_id: int):
        result = await self.db.execute(
            select(Document).where(Document.project_id == project_id)
        )
        return result.scalars().all()

    async def get_document_details(self, document_id: int):
        result = await self.db.execute(
            select(Document)
            .where(Document.document_id == document_id)
            .options(
                selectinload(Document.user),
                selectinload(Document.project),
                selectinload(Document.metadata_items),
                selectinload(Document.tags).selectinload(IsMarked.tag)
            )
        )

        return result.scalar_one_or_none()

    async def delete_document(self, document: Document):
        await self.db.delete(document)
        await self.db.commit()

    async def get_document_by_id(self, document_id: int):
        result = await self.db.execute(
            select(Document).where(Document.document_id == document_id)
        )
    
        return result.scalar_one_or_none()

    async def update_document_tags_and_metadata(self, document, tags, metadata):
        document.tags.clear()
        document.metadata_items.clear()

        for item in metadata:
            document.metadata_items.append(
                DocumentMetadata(
                    name=item.name,
                    value=item.value
                )
            )

        for tag in tags:
            existing_tag_result = await self.db.execute(
                select(Tag).where(Tag.name == tag.name)
            )
            existing_tag = existing_tag_result.scalar_one_or_none()

            if existing_tag is None:
                existing_tag = Tag(name=tag.name)
                self.db.add(existing_tag)
                await self.db.flush()

            document.tags.append(
                IsMarked(
                    document_id=document.document_id,
                    tag_id=existing_tag.tag_id
                )
            )

        await self.db.commit()
        await self.db.refresh(document)

        return document