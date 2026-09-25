AGGREGATOR_SYSTEM_PROMPT = """You are a senior compliance risk aggregator.
You will be given the findings from three specialist agents (KYC, Sanctions,
Market Risk) plus relevant excerpts from regulatory guidance.

Your job:
1. Weigh BOTH risk factors AND any mitigating/positive factors — a fair
   assessment considers reasons TO approve, not just reasons to reject.
2. If the specialist agents' findings seem inconsistent with each other
   (e.g. one flags a serious concern while another sees nothing), explicitly
   name that inconsistency in your rationale rather than silently averaging it away.
3. Ground your rationale in the regulatory excerpts provided where relevant.
4. Do not invent facts not present in the agent findings or regulations.

Respond ONLY with valid JSON in this exact format, no other text:
{
  "score": 0 to 100,
  "band": "low" | "medium" | "high",
  "rationale": "a few sentences explaining the score, referencing specific
                 findings and any conflicts or mitigating factors",
  "confidence": 0.0 to 1.0
}
"""


def build_aggregator_prompt(kyc_output: dict, sanctions_output: dict, market_risk_output: dict, regulations: list[dict]) -> str:
    reg_text = "\n\n".join(
        f"[{r['source_doc']}, relevance {r['relevance']}]: {r['chunk_text'][:400]}"
        for r in regulations
    ) or "No specific regulatory excerpts retrieved."

    return f"""KYC findings:
{kyc_output.get('summary', 'N/A')}
Flags: {kyc_output.get('flags', [])}
Confidence: {kyc_output.get('confidence', 'N/A')}

Sanctions findings:
{sanctions_output.get('summary', 'N/A')}
Requires manual review: {sanctions_output.get('requires_manual_review', 'N/A')}

Market Risk findings:
{market_risk_output.get('summary', 'N/A')}
Risk level: {market_risk_output.get('risk_level', 'N/A')}
Confidence: {market_risk_output.get('confidence', 'N/A')}

Relevant regulatory guidance:
{reg_text}

Provide your aggregated risk assessment."""