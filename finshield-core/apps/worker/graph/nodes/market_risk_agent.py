import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "..", "api"))

import json
import ollama
from datetime import datetime, timezone
from db import SessionLocal
from models.agent_run import AgentRun
from graph.state import CaseState
from services.market_data import get_company_overview
from prompts.market_risk_prompt import MARKET_RISK_SYSTEM_PROMPT, build_market_risk_prompt

# NOTE: Since not every loan applicant has a public stock ticker, this demo
# uses a fixed placeholder symbol so the pipeline always has real data to
# reason over. A production version would need a real symbol lookup step —
# worth stating plainly in the README as a known simplification.
DEMO_SYMBOL = "AAPL"


def market_risk_agent(state: CaseState) -> CaseState:
    db = SessionLocal()
    try:
        run = AgentRun(case_id=state["case_id"], agent_name="market_risk_agent", status="running")
        db.add(run)
        db.commit()
        db.refresh(run)

        market_data = get_company_overview(DEMO_SYMBOL)

        if not market_data:
            # Graceful degradation: if the free-tier rate limit is hit or the
            # symbol lookup fails, the case still completes honestly rather
            # than crashing or silently faking a result.
            output = {
                "summary": "Market data unavailable (API limit reached or symbol not found) — manual review recommended.",
                "risk_level": "unknown",
                "confidence": 0.0,
            }
        else:
            user_prompt = build_market_risk_prompt(market_data)
            response = ollama.chat(
                model="llama3.1:8b",
                messages=[
                    {"role": "system", "content": MARKET_RISK_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                format="json",
            )
            raw_content = response["message"]["content"]
            try:
                parsed = json.loads(raw_content)
            except json.JSONDecodeError:
                parsed = {
                    "risk_level": "unknown",
                    "summary": f"LLM returned unparseable output: {raw_content[:200]}",
                    "confidence": 0.0,
                }

            output = {
                "summary": parsed.get("summary", "No summary provided"),
                "risk_level": parsed.get("risk_level", "unknown"),
                "confidence": parsed.get("confidence", 0.5),
                "raw_market_data": market_data,   # stored for audit — the exact data grounding this narrative
            }

        run.status = "completed"
        run.output = output
        run.finished_at = datetime.now(timezone.utc)
        db.commit()
    finally:
        db.close()

    state["market_risk_output"] = output
    return state