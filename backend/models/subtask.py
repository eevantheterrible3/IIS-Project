import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class SubtaskStatus(str, enum.Enum):
    kreiran = "kreiran"
    u_toku = "u toku"
    zavrseno = "završeno"


class Subtask(Base):
    __tablename__ = "subtask"

    subtask_id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("task.task_id"))
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    deadline = Column(DateTime, nullable=True)
    current_status = Column(Enum(SubtaskStatus), default=SubtaskStatus.kreiran)
    assigned_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    task = relationship("Task", back_populates="subtasks")
    assigned_user = relationship("User", foreign_keys=[assigned_user_id])
    status_history = relationship("TaskStatusHistory", back_populates="subtask")
