from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    works = relationship("Work", back_populates="user")
    documents = relationship("Document", back_populates="user")
    activities = relationship("Activity", back_populates="user")
    allowed_permissions = relationship("Allows", back_populates="user")