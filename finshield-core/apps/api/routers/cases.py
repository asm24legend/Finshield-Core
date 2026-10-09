import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "worker"))

from tasks import run_case_pipeline
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import Response
from services.report_builder import build_compliance_report
from pydantic import BaseModel

from db import get_db
from models.case import Case
from models.entity import Entity
from models.agent_run import AgentRun
from schemas.case import CaseCreate, CaseRead
from models.risk_assessment import RiskAssessment as RiskAssessmentModel
from models.review import Review

class ReviewCreate(BaseModel):
    decision: str  # "approved" | "rejected" | "needs_info"
    reviewer_note: str | None = None

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
@router.get("/{case_id}/risk-assessment")
def get_risk_assessment(case_id: uuid.UUID, db: Session = Depends(get_db)):
    assessment = db.query(RiskAssessmentModel).filter(RiskAssessmentModel.case_id == case_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Risk assessment not yet available")
    return {
        "score": assessment.score,
        "band": assessment.band,
        "rationale": assessment.rationale,
    }
@router.get("/{case_id}/report")
def download_report(case_id: uuid.UUID, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    entity = db.query(Entity).filter(Entity.id == case.entity_id).first()
    runs = db.query(AgentRun).filter(AgentRun.case_id == case_id).order_by(AgentRun.started_at).all()
    assessment = db.query(RiskAssessmentModel).filter(RiskAssessmentModel.case_id == case_id).first()

    pdf_bytes = build_compliance_report(
        case={"id": str(case.id), "case_type": case.case_type},
        entity={"name": entity.name, "entity_type": entity.entity_type, "jurisdiction": entity.jurisdiction},
        agent_runs=[
            {"agent_name": r.agent_name, "status": r.status, "output": r.output}
            for r in runs
        ],
        risk_assessment={
            "score": assessment.score, "band": assessment.band, "rationale": assessment.rationale
        } if assessment else None,
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=case_{case_id}_report.pdf"},
    )

@router.post("/{case_id}/review")
def submit_review(case_id: uuid.UUID, payload: ReviewCreate, db: Session = Depends(get_db)):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    review = Review(
        case_id=case_id,
        decision=payload.decision,
        reviewer_note=payload.reviewer_note,
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    return {
        "id": str(review.id),
        "decision": review.decision,
        "reviewer_note": review.reviewer_note,
        "reviewed_at": review.reviewed_at,
    }


@router.get("/{case_id}/review")
def get_review(case_id: uuid.UUID, db: Session = Depends(get_db)):
    review = db.query(Review).filter(Review.case_id == case_id).order_by(Review.reviewed_at.desc()).first()
    if not review:
        raise HTTPException(status_code=404, detail="No review yet")
    return {
        "id": str(review.id),
        "decision": review.decision,
        "reviewer_note": review.reviewer_note,
        "reviewed_at": review.reviewed_at,
    }

@router.get("")
def list_cases(limit: int = 50, db: Session = Depends(get_db)):
    cases = db.query(Case).order_by(Case.created_at.desc()).limit(limit).all()
    case_ids = [c.id for c in cases]
    if not case_ids:
        return []

    entities = {e.id: e for e in db.query(Entity).filter(Entity.id.in_([c.entity_id for c in cases])).all()}
    assessments = {a.case_id: a for a in db.query(RiskAssessmentModel).filter(RiskAssessmentModel.case_id.in_(case_ids)).all()}

    # Newest review per case: rows come back newest-first, so keep the first one seen.
    reviews = {}
    for r in db.query(Review).filter(Review.case_id.in_(case_ids)).order_by(Review.reviewed_at.desc()).all():
        reviews.setdefault(r.case_id, r)

    return [
        {
            "id": str(c.id),
            "entity_name": entities[c.entity_id].name if c.entity_id in entities else "Unknown",
            "case_type": c.case_type,
            "status": c.status,
            "band": assessments[c.id].band if c.id in assessments else None,
            "score": assessments[c.id].score if c.id in assessments else None,
            "review_decision": reviews[c.id].decision if c.id in reviews else None,
            "created_at": c.created_at,
        }
        for c in cases
    ]