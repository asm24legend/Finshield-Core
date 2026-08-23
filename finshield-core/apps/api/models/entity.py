import uuid
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from db import Base


class Entity(Base):
    __tablename__ = "entities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    jurisdiction = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())