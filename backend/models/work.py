from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Work(Base):
    __tablename__ = "works"

    user_id = Column(String(36), ForeignKey("users.user_id"), primary_key=True)
    project_id = Column(String(36), ForeignKey("projects.project_id"), primary_key=True)
    role_id = Column(String(36), ForeignKey("roles.role_id"), nullable=False)

    user = relationship("User", back_populates="works")
    project = relationship("Project", back_populates="works")
    role = relationship("Role", back_populates="works")
