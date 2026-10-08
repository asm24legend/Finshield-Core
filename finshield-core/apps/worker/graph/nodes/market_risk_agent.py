import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "..", "api"))

import requests
from datetime import datetime, timezone
from db import SessionLocal
from models.agent_run import AgentRun
from models.entity import Entity
from models.case import Case
from graph.state import CaseState
from services.market_data import get_company_overview
from services.llm_client import chat_json
from prompts.market_risk_prompt import MARKET_RISK_SYSTEM_PROMPT, build_market_risk_prompt

# Known simplification (documented in README): corporations are assessed using
# a fixed demo ticker, since real company-name-to-ticker lookup is out of scope.
DEMO_SYMBOL = "AAPL"


def market_risk_agent(state: CaseState) -> CaseState:
    db = SessionLocal()
    try:
        run = AgentRun(case_id=state["case_id"], agent_name="market_risk_agent", status="running")
        db.add(run)
        db.commit()
        db.refresh(run)

        case = db.query(Case).filter(Case.id == state["case_id"]).first()
        entity = db.query(Entity).filter(Entity.id == case.entity_id).first()

        if entity.entity_type == "individual":
            # An honest "not applicable" beats silently reasoning about the wrong company.
            output = {
                "summary": "Market risk assessment not applicable: entity is an individual, not a publicly traded company.",
                "risk_level": "not_applicable",
                "confidence": 1.0,
                "degraded": False,
            }
        else:
            try:
                market_data = get_company_overview(DEMO_SYMBOL)
            except requests.RequestException:
                market_data = None  # network failure is treated like "data unavailable"

            if not market_data:
                output = {
                    "summary": "Market data unavailable (network error, API limit, or symbol not found). Manual review recommended.",
                    "risk_level": "unknown",
                    "confidence": 0.0,
                    "degraded": True,
                }
            else:
                user_prompt = build_market_risk_prompt(market_data)
                parsed = chat_json(
                    "llama3.1:8b", MARKET_RISK_SYSTEM_PROMPT, user_prompt,
                    fallback={"risk_level": "unknown", "summary": "Market risk AI assessment unavailable.", "confidence": 0.0},
                )
                output = {
                    "summary": parsed.get("summary", "No summary provided"),
                    "risk_level": parsed.get("risk_level", "unknown"),
                    "confidence": parsed.get("confidence", 0.5),
                    "raw_market_data": market_data,
                    "degraded": not parsed["llm_ok"],
                    "error": parsed.get("error"),
                }

        run.status = "completed"
        run.output = output
        run.finished_at = datetime.now(timezone.utc)
        db.commit()
    finally:
        db.close()

    state["market_risk_output"] = output
    return state