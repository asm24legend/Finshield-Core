import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "..", "api"))

from datetime import datetime, timezone
from db import SessionLocal
from models.agent_run import AgentRun
from models.risk_assessment import RiskAssessment
from graph.state import CaseState
from services.regulation_retrieval import find_relevant_regulations
from services.llm_client import chat_json
from prompts.aggregator_prompt import AGGREGATOR_SYSTEM_PROMPT, build_aggregator_prompt


def aggregator_agent(state: CaseState) -> CaseState:
    db = SessionLocal()
    try:
        run = AgentRun(case_id=state["case_id"], agent_name="aggregator_agent", status="running")
        db.add(run)
        db.commit()
        db.refresh(run)

        kyc_output = state.get("kyc_output", {})
        sanctions_output = state.get("sanctions_output", {})
        market_risk_output = state.get("market_risk_output", {})

        query_text = " ".join([
            kyc_output.get("summary", ""),
            sanctions_output.get("summary", ""),
            market_risk_output.get("summary", ""),
        ]).strip()

        try:
            regulations = find_relevant_regulations(db, query_text, top_k=3) if query_text else []
        except Exception:
            db.rollback()
            regulations = []  # retrieval failure shouldn't block the case; it's noted below

        user_prompt = build_aggregator_prompt(kyc_output, sanctions_output, market_risk_output, regulations)

        parsed = chat_json(
            "llama3.1:8b", AGGREGATOR_SYSTEM_PROMPT, user_prompt,
            fallback={"score": 50, "band": "medium", "rationale": "AI aggregation unavailable. Manual review required.", "confidence": 0.0},
        )

        score = parsed.get("score", 50)
        band = parsed.get("band", "medium")
        rationale = parsed.get("rationale", "No rationale provided")

        # --- Deterministic guardrails (plain code, applied after the LLM) ---
        degraded_agents = [
            name for name, out in [
                ("kyc", kyc_output), ("market_risk", market_risk_output)
            ] if out.get("degraded")
        ]
        if not parsed["llm_ok"]:
            degraded_agents.append("aggregator")

        sanctions_flagged = bool(sanctions_output.get("requires_manual_review"))
        requires_manual_review = sanctions_flagged or bool(degraded_agents)

        # A sanctions hit or a failed component must never end up labelled "low".
        if requires_manual_review and band == "low":
            band = "medium"
            rationale += " [Guardrail: band raised from low because a sanctions flag or degraded component requires manual review.]"

        final_output = {
            "score": score,
            "band": band,
            "rationale": rationale,
            "confidence": parsed.get("confidence", 0.5),
            "requires_manual_review": requires_manual_review,
            "degraded_components": degraded_agents,
            "regulations_cited": regulations,
            "error": parsed.get("error"),
        }

        assessment = RiskAssessment(
            case_id=state["case_id"],
            score=score,
            band=band,
            rationale=rationale,
            model_version="llama3.1:8b + nomic-embed-text",
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