import uuid
import enum

from sqlalchemy import Column, String, Integer, Enum
from sqlalchemy.orm import relationship

from database import Base


class ResourceStatus(str, enum.Enum):
    active = "active"
    not_active = "not_active"


class Resource(Base):
    __tablename__ = "resource"

    resource_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(Enum(ResourceStatus), default=ResourceStatus.active)
    total_quantity = Column(Integer, default=1)

    task_resources = relationship("TaskResource", back_populates="resource")
