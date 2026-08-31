import time
from datetime import datetime, timezone
from db import SessionLocal
from models.agent_run import AgentRun
from graph.state import CaseState


def sanctions_agent(state: CaseState) -> CaseState:
    db = SessionLocal()
    try:
        run = AgentRun(case_id=state["case_id"], agent_name="sanctions_agent", status="running")
        db.add(run)
        db.commit()
        db.refresh(run)

        time.sleep(2)
        output = {"summary": "Sanctions stub: no matches found", "requires_manual_review": False}

        run.status = "completed"
        run.output = output
        run.finished_at = datetime.now(timezone.utc)
        db.commit()
    finally:
        db.close()

    state["sanctions_output"] = output
    return state