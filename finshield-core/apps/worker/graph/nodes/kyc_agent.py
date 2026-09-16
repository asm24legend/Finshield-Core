import os
import sys
import json
import ollama
from datetime import datetime, timezone

# Add 'apps/api' to sys.path (3 directory levels up)
API_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "api")
)

if API_DIR not in sys.path:
    sys.path.insert(0, API_DIR)

from db import SessionLocal
from models.agent_run import AgentRun
from models.entity import Entity
from models.case import Case

from graph.state import CaseState
from services.kyc_features import compute_kyc_features
from prompts.kyc_prompt import KYC_SYSTEM_PROMPT, build_kyc_prompt


def kyc_agent(state: CaseState) -> CaseState:
    db = SessionLocal()
    run = None

    try:
        run = AgentRun(case_id=state["case_id"], agent_name="kyc_agent", status="running")
        db.add(run)
        db.commit()
        db.refresh(run)

        case = db.query(Case).filter(Case.id == state["case_id"]).first()
        if not case:
            raise ValueError(f"Case with ID {state['case_id']} not found.")

        entity = db.query(Entity).filter(Entity.id == case.entity_id).first()
        if not entity:
            raise ValueError(f"Entity with ID {case.entity_id} not found.")

        # Step 1: deterministic feature engineering
        features = compute_kyc_features(entity.name, entity.entity_type, entity.jurisdiction)

        # Step 2: LLM reasoning
        user_prompt = build_kyc_prompt(entity.name, entity.entity_type, entity.jurisdiction, features)

        response = ollama.chat(
            model="llama3.1:8b",
            messages=[
                {"role": "system", "content": KYC_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            format="json",
        )

        raw_content = response["message"]["content"]

        try:
            parsed = json.loads(raw_content)
        except json.JSONDecodeError:
            parsed = {
                "flags": [],
                "summary": f"LLM returned unparseable output: {raw_content[:200]}",
                "confidence": 0.0,
            }

        output = {
            "summary": parsed.get("summary", "No summary provided"),
            "flags": parsed.get("flags", []),
            "confidence": parsed.get("confidence", 0.5),
            "features": features,
            "prompt_used": user_prompt,
        }

        run.status = "completed"
        run.output = output
        run.finished_at = datetime.now(timezone.utc)
        db.commit()

        state["kyc_output"] = output

    except Exception as e:
        db.rollback()
        if run:
            run.status = "failed"
            run.output = {"error": str(e)}
            run.finished_at = datetime.now(timezone.utc)
            db.commit()
        raise e

    finally:
        db.close()

    return state