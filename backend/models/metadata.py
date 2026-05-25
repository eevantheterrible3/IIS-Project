import uuid
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class DocumentMetadata(Base):
    __tablename__ = "metadata"

    meta_data_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    document_id = Column(String(36), ForeignKey("documents.document_id"), nullable=False)
    name = Column(String(100), nullable=False)
    value = Column(Text)

    document = relationship("Document", back_populates="metadata_items")
