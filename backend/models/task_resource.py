import enum

from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class TaskResourceStatus(str, enum.Enum):
    free = "free"
    reserved = "reserved"
    in_use = "in_use"


class TaskResource(Base):
    __tablename__ = "task_resource"

    task_id = Column(String(36), ForeignKey("task.task_id"), primary_key=True)
    resource_id = Column(String(36), ForeignKey("resource.resource_id"), primary_key=True)
    quantity = Column(Integer, default=1)
    reserved_from = Column(DateTime, nullable=True)
    reserved_until = Column(DateTime, nullable=True)
    status = Column(Enum(TaskResourceStatus), default=TaskResourceStatus.free)

    task = relationship("Task", back_populates="resources")
    resource = relationship("Resource", back_populates="task_resources")
