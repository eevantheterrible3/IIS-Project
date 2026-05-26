import uuid
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class WorkflowInstanceStep(Base):
    __tablename__ = "workflow_instance_steps"

    instance_step_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    instance_id = Column(String(36), ForeignKey("workflow_instances.instance_id", ondelete="CASCADE"), nullable=False)
    action_id = Column(String(36), ForeignKey("workflow_actions.action_id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), nullable=False, default="pending")
    progress = Column(Integer, nullable=False, default=0)
    assigned_user_id = Column(String(36), ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    note = Column(Text, nullable=True)

    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    instance = relationship("WorkflowInstance", back_populates="steps")
    action = relationship("WorkflowAction")
    assigned_user = relationship("User")
