import enum
import uuid
from sqlalchemy import Column, String, Text, DateTime, Enum
from sqlalchemy.orm import relationship
from database import Base


class ProjectStatus(enum.Enum):
    ACTIVE = "active"
    FINISHED = "finished"


class Project(Base):
    __tablename__ = "projects"

    project_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    status = Column(Enum(ProjectStatus), nullable=False, default=ProjectStatus.ACTIVE)

    works = relationship("Work", back_populates="project")
    documents = relationship("Document", back_populates="project")
