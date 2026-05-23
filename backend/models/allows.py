from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Allows(Base):
    __tablename__ = "allows"

    user_id = Column(String(36), ForeignKey("users.user_id"), primary_key=True)
    document_id = Column(String(36), ForeignKey("documents.document_id"), primary_key=True)
    permission_id = Column(String(36), ForeignKey("permissions.permission_id"), primary_key=True)

    user = relationship("User", back_populates="allowed_permissions")
    document = relationship("Document", back_populates="allowed_users")
    permission = relationship("Permission", back_populates="allowed_users")
