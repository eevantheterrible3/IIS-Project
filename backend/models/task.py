import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class TaskPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Task(Base):
    __tablename__ = "task"

    task_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    priority = Column(Enum(TaskPriority), nullable=True)
    current_step_id = Column(Integer, ForeignKey("task_workflow_step.step_id"), nullable=True)
    task_workflow_id = Column(Integer, ForeignKey("task_workflow.task_workflow_id"))
    deadline = Column(DateTime, nullable=True)
    assigned_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    last_updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    project_id = Column(Integer, ForeignKey("projects.project_id"))

    workflow = relationship("TaskWorkflow", back_populates="tasks")
    current_step = relationship("TaskWorkflowStep", foreign_keys=[current_step_id])
    assigned_user = relationship("User", foreign_keys=[assigned_user_id])
    project = relationship("Project")
    subtasks = relationship("Subtask", back_populates="task")
    status_history = relationship("TaskStatusHistory", back_populates="task")
    resources = relationship("TaskResource", back_populates="task")
