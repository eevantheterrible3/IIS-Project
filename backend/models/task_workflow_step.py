import uuid

from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class TaskWorkflowStep(Base):
    __tablename__ = "task_workflow_step"

    step_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    task_workflow_id = Column(String(36), ForeignKey("task_workflow.task_workflow_id"))
    status_name = Column(String, nullable=False)
    next_step_id = Column(String(36), ForeignKey("task_workflow_step.step_id"), nullable=True)
    is_first = Column(Boolean, default=False)
    is_last = Column(Boolean, default=False)

    workflow = relationship("TaskWorkflow", back_populates="steps", foreign_keys=[task_workflow_id])
    next_step = relationship("TaskWorkflowStep", remote_side="TaskWorkflowStep.step_id")
