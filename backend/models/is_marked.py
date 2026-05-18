from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class IsMarked(Base):
    __tablename__ = "is_marked"

    document_id = Column(Integer, ForeignKey("documents.document_id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.tag_id"), primary_key=True)

    document = relationship("Document", back_populates="tags")
    tag = relationship("Tag", back_populates="marked_documents")