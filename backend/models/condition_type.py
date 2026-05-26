import uuid
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from database import Base


class ConditionType(Base):
    __tablename__ = "condition_types"

    condition_type_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(200), nullable=False)

    conditions = relationship("Condition", back_populates="condition_type")
