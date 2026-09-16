KYC_SYSTEM_PROMPT = """You are a KYC (Know Your Customer) compliance assistant.
You will be given an entity's data AND a set of pre-computed risk indicator flags.
Your job is to write a short, plain-language assessment based ONLY on what's given.
Do not invent facts not present in the input.

Respond ONLY with valid JSON in this exact format, no other text:
{
  "flags": ["short bullet describing any inconsistency or risk factor found"],
  "summary": "one or two sentence plain-language summary",
  "confidence": 0.0 to 1.0
}
If there are no flags, use an empty list: "flags": []
"confidence" reflects how certain you are in this assessment given the
available data — lower it if the input data is sparse or ambiguous.
"""


def build_kyc_prompt(entity_name: str, entity_type: str, jurisdiction: str | None, features: dict) -> str:
    return f"""Entity name: {entity_name}
Entity type: {entity_type}
Jurisdiction: {jurisdiction or "not provided"}

Pre-computed risk indicators:
- Missing jurisdiction: {features['missing_jurisdiction']}
- Generic/placeholder-like name pattern: {features['generic_name_pattern']}
- Entity type recognized as valid category: {features['entity_type_recognized']}

Write a KYC assessment based on this entity's data and the risk indicators above."""