import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "..", "api"))

from datetime import datetime, timezone
from db import SessionLocal
from models.agent_run import AgentRun
from models.entity import Entity
from models.case import Case
from graph.state import CaseState
from services.kyc_features import compute_kyc_features
from services.llm_client import chat_json
from prompts.kyc_prompt import KYC_SYSTEM_PROMPT, build_kyc_prompt


def kyc_agent(state: CaseState) -> CaseState:
    db = SessionLocal()
    try:
        run = AgentRun(case_id=state["case_id"], agent_name="kyc_agent", status="running")
        db.add(run)
        db.commit()
        db.refresh(run)

        case = db.query(Case).filter(Case.id == state["case_id"]).first()
        entity = db.query(Entity).filter(Entity.id == case.entity_id).first()

        features = compute_kyc_features(entity.name, entity.entity_type, entity.jurisdiction)
        user_prompt = build_kyc_prompt(entity.name, entity.entity_type, entity.jurisdiction, features)

        parsed = chat_json(
            "llama3.1:8b", KYC_SYSTEM_PROMPT, user_prompt,
            fallback={"flags": [], "summary": "KYC AI assessment unavailable. Manual review required.", "confidence": 0.0},
        )

        output = {
            "summary": parsed.get("summary", "No summary provided"),
            "flags": parsed.get("flags", []),
            "confidence": parsed.get("confidence", 0.5),
            "features": features,
            "prompt_used": user_prompt,
            "degraded": not parsed["llm_ok"],
            "error": parsed.get("error"),
        }

        run.status = "completed"
        run.output = output
        run.finished_at = datetime.now(timezone.utc)
        db.commit()
    finally:
        db.close()

    state["kyc_output"] = output
    return state