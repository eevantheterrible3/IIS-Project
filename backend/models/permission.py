import uuid
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from database import Base


class Permission(Base):
    __tablename__ = "permissions"

    permission_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)

    allowed_users = relationship("Allows", back_populates="permission")
