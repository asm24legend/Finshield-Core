import uuid
from datetime import datetime
from pydantic import BaseModel


class CaseCreate(BaseModel):
    """Shape of the request body for POST /cases."""
    entity_id: uuid.UUID
    case_type: str


class CaseRead(BaseModel):
    """Shape of the response for GET /cases/{id} and POST /cases."""
    id: uuid.UUID
    entity_id: uuid.UUID
    case_type: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True