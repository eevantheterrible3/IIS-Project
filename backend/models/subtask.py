import uuid
import enum
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class SubtaskStatus(str, enum.Enum):
    created = "created"
    in_progress = "in_progress"
    done = "done"


class Subtask(Base):
    __tablename__ = "subtask"

    subtask_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    task_id = Column(String(36), ForeignKey("task.task_id"))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    deadline = Column(DateTime, nullable=True)
    current_status = Column(Enum(SubtaskStatus), default=SubtaskStatus.created)
    assigned_user_id = Column(String(36), ForeignKey("users.user_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    task = relationship("Task", back_populates="subtasks")
    assigned_user = relationship("User", foreign_keys=[assigned_user_id])
    status_history = relationship("TaskStatusHistory", back_populates="subtask")
