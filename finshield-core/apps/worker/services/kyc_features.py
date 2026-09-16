def compute_kyc_features(entity_name: str, entity_type: str, jurisdiction: str | None) -> dict:
    """
    Derives simple, deterministic risk indicators from entity data BEFORE
    any LLM reasoning happens. This is the "Feature Engineer" step —
    structured facts computed by plain code, not asked of the LLM.

    Why this matters: an LLM asked "does this look risky?" on raw fields
    will sometimes miss simple facts (e.g., a blank jurisdiction) or
    inconsistently notice them across runs. Computing these deterministically
    means the same input always produces the same base facts, and the LLM's
    job becomes "reason over these confirmed facts" rather than
    "first notice the facts, then reason about them" — a smaller, more
    reliable task for a small local model.
    """
    features = {
        "missing_jurisdiction": jurisdiction is None or jurisdiction.strip() == "",
        "generic_name_pattern": entity_name.strip().lower() in {
            "test corp", "acme corp", "company", "n/a", "unknown"
        },
        "entity_type_recognized": entity_type in {"individual", "corporation"},
    }
    return features