from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    document_version_id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.document_id", ondelete="CASCADE"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    version_number = Column(Integer, nullable=False)
    full_content = Column(Text)
    note = Column(String(500))

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    document = relationship("Document", back_populates="versions")
    author = relationship("User", back_populates="document_versions")
