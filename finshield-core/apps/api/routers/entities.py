import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db
from models.entity import Entity
from schemas.entity import EntityCreate, EntityRead

router = APIRouter(prefix="/entities", tags=["entities"])


@router.post("", response_model=EntityRead)
def create_entity(payload: EntityCreate, db: Session = Depends(get_db)):
    entity = Entity(
        name=payload.name,
        entity_type=payload.entity_type,
        jurisdiction=payload.jurisdiction,
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return entity


@router.get("/{entity_id}", response_model=EntityRead)
def get_entity(entity_id: uuid.UUID, db: Session = Depends(get_db)):
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity