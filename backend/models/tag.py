from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class Tag(Base):
    __tablename__ = "tags"

    tag_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)

    marked_documents = relationship("IsMarked", back_populates="tag", cascade="all, delete-orphan")