import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from db import Base


class Review(Base):
    """A human reviewer's decision on a case, recorded for audit and override tracking."""
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False)
    decision = Column(String, nullable=False)  # "approved" | "rejected" | "needs_info"
    reviewer_note = Column(Text, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), server_default=func.now())