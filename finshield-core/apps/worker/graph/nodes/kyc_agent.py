import os
import sys
import json
import uuid
from datetime import datetime, timezone
from ollama import Client

# -----------------------------------------------------------------------------
# Dynamic Path Setup
# -----------------------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
API_DIR = os.path.join(BASE_DIR, "api")
WORKER_DIR = os.path.join(BASE_DIR, "worker")

for path in (API_DIR, WORKER_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

from db import SessionLocal
from models.agent_run import AgentRun
from models.entity import Entity
from models.case import Case

from graph.state import CaseState
from services.kyc_features import compute_kyc_features
from prompts.kyc_prompt import KYC_SYSTEM_PROMPT, build_kyc_prompt

# -----------------------------------------------------------------------------
# Agent Node
# -----------------------------------------------------------------------------
def kyc_agent(state: CaseState) -> CaseState:
    db = SessionLocal()
    run = None

    try:
        # Cast case_id string to UUID safely
        raw_case_id = state["case_id"]
        case_id = uuid.UUID(str(raw_case_id)) if isinstance(raw_case_id, str) else raw_case_id

        # 1. Audit tracking entry
        run = AgentRun(
            case_id=case_id, 
            agent_name="kyc_agent", 
            status="running"
        )
        db.add(run)
        db.commit()
        db.refresh(run)

        # 2. Fetch database entities
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            raise ValueError(f"Case with ID '{case_id}' not found.")

        entity = db.query(Entity).filter(Entity.id == case.entity_id).first()
        if not entity:
            raise ValueError(f"Entity with ID '{case.entity_id}' not found.")

        # 3. Deterministic feature engineering
        features = compute_kyc_features(
            entity.name, 
            entity.entity_type, 
            entity.jurisdiction
        )

        # 4. Prompt construction
        user_prompt = build_kyc_prompt(
            entity.name, 
            entity.entity_type, 
            entity.jurisdiction, 
            features
        )

        # 5. LLM Call with 120s timeout and lighter model for RTX 2050
        client = Client(host="http://127.0.0.1:11434", timeout=120.0)
        
        try:
            response = client.chat(
                model="llama3.2:3b",
                messages=[
                    {"role": "system", "content": KYC_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                format="json",
            )
            raw_content = response["message"]["content"]
            parsed = json.loads(raw_content)
        except Exception as llm_err:
            parsed = {
                "flags": ["LLM_EXECUTION_FAILURE"],
                "summary": f"Inference failed or timed out: {str(llm_err)}",
                "confidence": 0.0,
            }

        output = {
            "summary": parsed.get("summary", "No summary provided"),
            "flags": parsed.get("flags", []),
            "confidence": parsed.get("confidence", 0.5),
            "features": features,
            "prompt_used": user_prompt,
        }

        # 6. Mark node run as completed
        run.status = "completed"
        run.output = output
        run.finished_at = datetime.now(timezone.utc)
        db.commit()

        # 7. Update graph state
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