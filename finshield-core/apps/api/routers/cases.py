import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "worker"))

from tasks import run_case_pipeline
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import get_db
from models.case import Case
from models.entity import Entity
from models.agent_run import AgentRun
from schemas.case import CaseCreate, CaseRead

router = APIRouter(prefix="/cases", tags=["cases"])


@router.post("", response_model=CaseRead)
def create_case(payload: CaseCreate, db: Session = Depends(get_db)):
    entity = db.query(Entity).filter(Entity.id == payload.entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    case = Case(
        entity_id=payload.entity_id,
        case_type=payload.case_type,
        status="pending",
    )
    db.add(case)
    db.commit()
    db.refresh(case)

    run_case_pipeline.delay(str(case.id))  # enqueue background processing

    return case


@router.get("/{case_id}", response_model=CaseRead)
def get_case(case_id: uuid.UUID, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.get("/{case_id}/agent-runs")
def get_agent_runs(case_id: uuid.UUID, db: Session = Depends(get_db)):
    runs = db.query(AgentRun).filter(AgentRun.case_id == case_id).order_by(AgentRun.started_at).all()
    return [
        {
            "agent_name": r.agent_name,
            "status": r.status,
            "output": r.output,
            "started_at": r.started_at,
            "finished_at": r.finished_at,
        }
        for r in runs
    ]