import uuid
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from db import Base


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False)
    score = Column(Integer, nullable=False)
    band = Column(String, nullable=False)
    rationale = Column(String, nullable=True)
    model_version = Column(String, nullable=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())