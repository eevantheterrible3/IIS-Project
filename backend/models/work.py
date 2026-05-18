from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Work(Base):
    __tablename__ = "works"

    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.role_id"), nullable=False)

    user = relationship("User", back_populates="works")
    project = relationship("Project", back_populates="works")
    role = relationship("Role", back_populates="works")