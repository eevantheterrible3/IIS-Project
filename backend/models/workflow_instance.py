import uuid
from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class WorkflowInstance(Base):
    __tablename__ = "workflow_instances"

    instance_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    workflow_id = Column(String(36), ForeignKey("workflows.workflow_id", ondelete="CASCADE"), nullable=False)
    document_id = Column(String(36), ForeignKey("documents.document_id", ondelete="CASCADE"), nullable=False)
    current_step_id = Column(String(36), ForeignKey("workflow_actions.action_id", ondelete="SET NULL"), nullable=True)
    designated_user_id = Column(String(36), ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    note = Column(Text, nullable=True)

    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)

    workflow = relationship("Workflow", back_populates="instances")
    document = relationship("Document")
    current_step = relationship("WorkflowAction")
    designated_user = relationship("User")
    steps = relationship("WorkflowInstanceStep", back_populates="instance", cascade="all, delete-orphan")
