import uuid
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class DocumentSection(Base):
    __tablename__ = "document_sections"

    document_section_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    document_id = Column(String(36), ForeignKey("documents.document_id", ondelete="CASCADE"), nullable=False)
    section_template_id = Column(String(36), ForeignKey("section_templates.section_template_id", ondelete="SET NULL"), nullable=True)
    content = Column(Text)
    order_index = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    document = relationship("Document", back_populates="sections")
    section_template = relationship("SectionTemplate", back_populates="document_sections")
