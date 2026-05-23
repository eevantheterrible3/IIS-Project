from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class DocumentType(Base):
    __tablename__ = "document_types"

    document_type_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text)
    system_prompt = Column(Text)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    section_templates = relationship("SectionTemplate", back_populates="document_type")
    documents = relationship("Document", back_populates="document_type")
