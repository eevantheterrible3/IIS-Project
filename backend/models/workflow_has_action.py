from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class WorkflowHasAction(Base):
    __tablename__ = "workflow_has_actions"

    workflow_id = Column(String(36), ForeignKey("workflows.workflow_id", ondelete="CASCADE"), primary_key=True)
    action_id = Column(String(36), ForeignKey("workflow_actions.action_id", ondelete="CASCADE"), primary_key=True)
    next_action = Column(String(36), ForeignKey("workflow_actions.action_id", ondelete="SET NULL"), nullable=True)
    is_start_step = Column(Boolean, nullable=False, default=False)
    condition_id = Column(String(36), ForeignKey("conditions.condition_id", ondelete="SET NULL"), nullable=True)

    workflow = relationship("Workflow", back_populates="workflow_actions")
    action = relationship("WorkflowAction", back_populates="workflow_links", foreign_keys=[action_id])
    next_action_ref = relationship("WorkflowAction", foreign_keys=[next_action])
    condition = relationship("Condition")
