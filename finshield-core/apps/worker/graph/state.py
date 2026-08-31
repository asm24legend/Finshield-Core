from typing import TypedDict, Optional


class CaseState(TypedDict):
    case_id: str
    kyc_output: Optional[dict]
    sanctions_output: Optional[dict]
    market_risk_output: Optional[dict]
    final_output: Optional[dict]