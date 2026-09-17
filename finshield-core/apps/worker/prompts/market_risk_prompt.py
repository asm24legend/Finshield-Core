MARKET_RISK_SYSTEM_PROMPT = """You are a market risk analyst assistant.
You will be given real financial data for a company. Write a short risk narrative
based ONLY on the numbers provided. Do not invent figures not given to you.

Respond ONLY with valid JSON in this exact format, no other text:
{
  "risk_level": "low" | "medium" | "high",
  "summary": "two to three sentence narrative referencing the actual data given",
  "confidence": 0.0 to 1.0
}
"confidence" reflects how certain you are given the available data —
lower it if key figures are missing or the data is incomplete.
"""


def build_market_risk_prompt(market_data: dict) -> str:
    return f"""Company: {market_data.get('name')}
Sector: {market_data.get('sector')}
Market cap: {market_data.get('market_cap')}
P/E ratio: {market_data.get('pe_ratio')}
Beta (volatility vs market): {market_data.get('beta')}
Profit margin: {market_data.get('profit_margin')}

Assess the market risk level based on these figures."""