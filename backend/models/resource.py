import enum

from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class ResourceStatus(str, enum.Enum):
    aktivan = "aktivan"
    neaktivan = "neaktivan"


class Resource(Base):
    __tablename__ = "resource"

    resource_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(Enum(ResourceStatus), default=ResourceStatus.aktivan)
    total_quantity = Column(Integer, default=1)

    task_resources = relationship("TaskResource", back_populates="resource")
