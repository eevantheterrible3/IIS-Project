from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Document(Base):
    __tablename__ = "documents"

    document_id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.project_id"), nullable=False)

    name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)
    user_prompt = Column(Text)
    status = Column(String(50), nullable=False, default="draft")


    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    user = relationship("User", back_populates="documents")
    project = relationship("Project", back_populates="documents")

    metadata_items = relationship("DocumentMetadata", back_populates="document", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="document", cascade="all, delete-orphan")
    tags = relationship("IsMarked", back_populates="document", cascade="all, delete-orphan")
    allowed_users = relationship("Allows", back_populates="document", cascade="all, delete-orphan")