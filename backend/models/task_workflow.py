import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class TaskWorkflow(Base):
    __tablename__ = "task_workflow"

    task_workflow_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    created_by = Column(String(36), ForeignKey("users.user_id"))

    steps = relationship("TaskWorkflowStep", back_populates="workflow", foreign_keys="TaskWorkflowStep.task_workflow_id")
    tasks = relationship("Task", back_populates="workflow")
