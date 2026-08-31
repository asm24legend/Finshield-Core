import time
from datetime import datetime, timezone
from db import SessionLocal
from models.agent_run import AgentRun
from graph.state import CaseState


def market_risk_agent(state: CaseState) -> CaseState:
    db = SessionLocal()
    try:
        run = AgentRun(case_id=state["case_id"], agent_name="market_risk_agent", status="running")
        db.add(run)
        db.commit()
        db.refresh(run)

        time.sleep(2)
        output = {"summary": "Market risk stub: moderate volatility in sector"}

        run.status = "completed"
        run.output = output
        run.finished_at = datetime.now(timezone.utc)
        db.commit()
    finally:
        db.close()

    state["market_risk_output"] = output
    return state