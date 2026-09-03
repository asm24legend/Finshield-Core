import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "..", "api"))

from datetime import datetime, timezone
from db import SessionLocal
from models.agent_run import AgentRun
from models.entity import Entity
from models.case import Case
from graph.state import CaseState
from services.fuzzy_match import check_sanctions


def sanctions_agent(state: CaseState) -> CaseState:
    db = SessionLocal()
    try:
        run = AgentRun(case_id=state["case_id"], agent_name="sanctions_agent", status="running")
        db.add(run)
        db.commit()
        db.refresh(run)

        case = db.query(Case).filter(Case.id == state["case_id"]).first()
        entity = db.query(Entity).filter(Entity.id == case.entity_id).first()

        result = check_sanctions(db, entity.name)

        top_match = result["candidates"][0] if result["candidates"] else None
        output = {
            "summary": (
                f"Potential match found: {top_match['name']} ({top_match['match_score']}% similarity)"
                if result["requires_manual_review"]
                else "No significant sanctions matches found"
            ),
            "requires_manual_review": result["requires_manual_review"],
            "candidates": result["candidates"][:5],
        }

        run.status = "completed"
        run.output = output
        run.finished_at = datetime.now(timezone.utc)
        db.commit()
    finally:
        db.close()

    state["sanctions_output"] = output
    return state