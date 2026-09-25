import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "..", "api"))

import json
import ollama
from datetime import datetime, timezone
from db import SessionLocal
from models.agent_run import AgentRun
from models.risk_assessment import RiskAssessment
from graph.state import CaseState
from services.regulation_retrieval import find_relevant_regulations
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

        # Build a query string from the case's findings so far, to retrieve
        # the most relevant regulatory context for THIS specific case.
        query_text = " ".join([
            kyc_output.get("summary", ""),
            sanctions_output.get("summary", ""),
            market_risk_output.get("summary", ""),
        ]).strip()

        regulations = find_relevant_regulations(db, query_text, top_k=3) if query_text else []

        user_prompt = build_aggregator_prompt(kyc_output, sanctions_output, market_risk_output, regulations)

        response = ollama.chat(
            model="llama3.1:8b",
            messages=[
                {"role": "system", "content": AGGREGATOR_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            format="json",
        )

        raw_content = response["message"]["content"]
        try:
            parsed = json.loads(raw_content)
        except json.JSONDecodeError:
            parsed = {
                "score": 50,
                "band": "medium",
                "rationale": f"LLM returned unparseable output: {raw_content[:200]}",
                "confidence": 0.0,
            }

        final_output = {
            "score": parsed.get("score", 50),
            "band": parsed.get("band", "medium"),
            "rationale": parsed.get("rationale", "No rationale provided"),
            "confidence": parsed.get("confidence", 0.5),
            "regulations_cited": regulations,   # exact chunks used, for audit
        }

        assessment = RiskAssessment(
            case_id=state["case_id"],
            score=final_output["score"],
            band=final_output["band"],
            rationale=final_output["rationale"],
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