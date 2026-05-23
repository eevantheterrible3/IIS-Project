from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class SectionTemplate(Base):
    __tablename__ = "section_templates"

    section_template_id = Column(Integer, primary_key=True, index=True)
    document_type_id = Column(Integer, ForeignKey("document_types.document_type_id", ondelete="SET NULL"), nullable=True)
    name = Column(String(150), nullable=False)
    content_structure = Column(Text)
    system_prompt = Column(Text)
    order_index = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    document_type = relationship("DocumentType", back_populates="section_templates")
    document_sections = relationship("DocumentSection", back_populates="section_template")
