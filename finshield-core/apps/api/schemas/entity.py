import uuid
from datetime import datetime
from pydantic import BaseModel


class EntityCreate(BaseModel):
    """Shape of the request body for POST /entities."""
    name: str
    entity_type: str
    jurisdiction: str | None = None


class EntityRead(BaseModel):
    """Shape of the response for GET /entities/{id} and POST /entities."""
    id: uuid.UUID
    name: str
    entity_type: str
    jurisdiction: str | None
    created_at: datetime

    class Config:
        from_attributes = True