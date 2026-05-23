import uuid
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from database import Base


class Tag(Base):
    __tablename__ = "tags"

    tag_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(100), nullable=False, unique=True)

    marked_documents = relationship("IsMarked", back_populates="tag", cascade="all, delete-orphan")
