import uuid
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from database import Base


class WorkflowAction(Base):
    __tablename__ = "workflow_actions"

    action_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(200), nullable=False)
    type = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)

    workflow_links = relationship("WorkflowHasAction", back_populates="action", foreign_keys="[WorkflowHasAction.action_id]")
