from sqlalchemy import text
from rapidfuzz import fuzz

SIMILARITY_THRESHOLD = 0.3      # pg_trgm's initial candidate filter (loose, catches more)
REVIEW_THRESHOLD = 75           # rapidfuzz score (0-100) above which we flag for manual review


def find_sanctions_candidates(db, query_name: str, limit: int = 10):
    """
    Step 1: use pg_trgm's trigram similarity for a fast first-pass filter
    directly in Postgres (fast even across tens of thousands of rows,
    thanks to the GIN index from Day 1).
    """
    result = db.execute(
        text("""
            SELECT id, name, entry_type, program,
                   similarity(name, :query_name) AS trgm_score
            FROM sanctions_entries
            WHERE name % :query_name
            ORDER BY trgm_score DESC
            LIMIT :limit
        """),
        {"query_name": query_name, "limit": limit},
    )
    candidates = []
    for row in result:
        row_dict = dict(row._mapping)
        row_dict["id"] = str(row_dict["id"])  # UUID -> string, so it's JSON-serializable downstream
        candidates.append(row_dict)
    return candidates


def score_candidates(query_name: str, candidates: list[dict]) -> list[dict]:
    """
    Step 2: re-score the (already-narrowed) candidates with rapidfuzz for a
    more precise, human-interpretable similarity score (0-100).
    """
    scored = []
    for c in candidates:
        score = fuzz.token_sort_ratio(query_name.lower(), c["name"].lower())
        scored.append({**c, "match_score": round(score, 1)})
    return sorted(scored, key=lambda x: x["match_score"], reverse=True)


def check_sanctions(db, entity_name: str) -> dict:
    candidates = find_sanctions_candidates(db, entity_name)
    scored = score_candidates(entity_name, candidates)

    requires_review = any(
        c["match_score"] >= REVIEW_THRESHOLD or c["trgm_score"] >= 0.5
        for c in scored
    )

    return {
        "query_name": entity_name,
        "candidates": scored,
        "requires_manual_review": requires_review,
    }