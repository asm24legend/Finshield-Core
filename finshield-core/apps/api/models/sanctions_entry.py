import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from db import Base


class SanctionsEntry(Base):
    """A single entry from a sanctions list (e.g. OFAC's SDN list)."""
    __tablename__ = "sanctions_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)  # primary listed name
    entry_type = Column(String, nullable=True)          # "individual" | "entity"
    program = Column(String, nullable=True)              # e.g. "SDGT", "UKRAINE-EO13662"
    source_id = Column(String, nullable=True)            # OFAC's own internal ID for this entry