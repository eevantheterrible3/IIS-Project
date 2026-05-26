import uuid
from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Condition(Base):
    __tablename__ = "conditions"

    condition_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    condition_type_id = Column(String(36), ForeignKey("condition_types.condition_type_id", ondelete="SET NULL"), nullable=True)
    document_type_id = Column(String(36), ForeignKey("document_types.document_type_id", ondelete="SET NULL"), nullable=True)
    role_id = Column(String(36), ForeignKey("roles.role_id", ondelete="SET NULL"), nullable=True)
    description = Column(Text, nullable=True)

    condition_type = relationship("ConditionType", back_populates="conditions")
    document_type = relationship("DocumentType")
    role = relationship("Role")
