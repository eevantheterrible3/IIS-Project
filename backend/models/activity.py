import enum

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum
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

    activity_id = Column(Integer, primary_key=True, index=True)

    document_id = Column(Integer, ForeignKey("documents.document_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    type = Column(Enum(ActivityType), nullable=False)
    date = Column(DateTime, server_default=func.now())

    document = relationship("Document", back_populates="activities")
    user = relationship("User", back_populates="activities")