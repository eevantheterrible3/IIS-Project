import enum
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class ActivityType(enum.Enum):
    DELETE = "delete"
    CREATE = "create"
    UPDATE = "update"
    VIEW = "view"


class Activity(Base):
    __tablename__ = "activities"

    activity_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    document_id = Column(String(36), ForeignKey("documents.document_id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)
    type = Column(Enum(ActivityType), nullable=False)
    date = Column(DateTime, server_default=func.now())

    document = relationship("Document", back_populates="activities")
    user = relationship("User", back_populates="activities")
