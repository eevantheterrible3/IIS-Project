from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class DocumentMetadata(Base):
    __tablename__ = "metadata"

    meta_data_id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.document_id"), nullable=False)

    name = Column(String(100), nullable=False)
    value = Column(Text)

    document = relationship("Document", back_populates="metadata_items")