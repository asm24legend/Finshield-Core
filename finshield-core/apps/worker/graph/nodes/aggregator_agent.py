import time
from datetime import datetime, timezone
from db import SessionLocal
from models.agent_run import AgentRun
from models.risk_assessment import RiskAssessment
from graph.state import CaseState


def aggregator_agent(state: CaseState) -> CaseState:
    db = SessionLocal()
    try:
        run = AgentRun(case_id=state["case_id"], agent_name="aggregator_agent", status="running")
        db.add(run)
        db.commit()
        db.refresh(run)

        time.sleep(1)
        print("MARKER_AGGREGATOR_V2_RUNNING")

        final_output = {
            "score": 35,
            "band": "low",
            "rationale": "Aggregated stub output from KYC, Sanctions, and Market Risk agents.",
        }

        assessment = RiskAssessment(
            case_id=state["case_id"],
            score=final_output["score"],
            band=final_output["band"],
            rationale=final_output["rationale"],
            model_version="stub-v0",
        )
        db.add(assessment)

        run.status = "completed"
        run.output = final_output
        run.finished_at = datetime.now(timezone.utc)
        db.commit()
    finally:
        db.close()

    state["final_output"] = final_output
    return state