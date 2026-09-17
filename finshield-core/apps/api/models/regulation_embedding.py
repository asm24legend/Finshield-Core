import uuid
from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector
from db import Base


class RegulationEmbedding(Base):
    """A chunk of regulatory text with its embedding vector, for similarity search."""
    __tablename__ = "regulation_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_doc = Column(String, nullable=False)      # e.g. "FinCEN SAR Guidance"
    chunk_text = Column(Text, nullable=False)
    embedding = Column(Vector(768), nullable=False)   # dimension depends on the embedding model, see Step 3
    doc_metadata = Column(JSONB, nullable=True)