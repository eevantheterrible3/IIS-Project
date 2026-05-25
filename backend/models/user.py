import uuid
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    username = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    works = relationship("Work", back_populates="user")
    documents = relationship("Document", back_populates="user")
    activities = relationship("Activity", back_populates="user")
    allowed_permissions = relationship("Allows", back_populates="user")
    document_versions = relationship("DocumentVersion", back_populates="author")
    document_ratings = relationship("DocumentRating", back_populates="user")
