import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class TaskStatusHistory(Base):
    __tablename__ = "task_status_history"

    history_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    task_id = Column(String(36), ForeignKey("task.task_id"))
    subtask_id = Column(String(36), ForeignKey("subtask.subtask_id"), nullable=True)
    old_step_id = Column(String(36), ForeignKey("task_workflow_step.step_id"), nullable=True)
    new_step_id = Column(String(36), ForeignKey("task_workflow_step.step_id"))
    changed_by_user_id = Column(String(36), ForeignKey("users.user_id"))
    changed_at = Column(DateTime, default=datetime.now)

    task = relationship("Task", back_populates="status_history")
    subtask = relationship("Subtask", back_populates="status_history")
    changed_by = relationship("User", foreign_keys=[changed_by_user_id])
