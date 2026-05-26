import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Workflow(Base):
    __tablename__ = "workflows"

    workflow_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(200), nullable=False)
    created_by = Column(String(36), ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    creator = relationship("User", back_populates="workflows")
    workflow_actions = relationship("WorkflowHasAction", back_populates="workflow", cascade="all, delete-orphan")
    instances = relationship("WorkflowInstance", back_populates="workflow", cascade="all, delete-orphan")
