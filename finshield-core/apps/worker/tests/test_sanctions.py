import json
from db import SessionLocal
from services.fuzzy_match import check_sanctions


def _check(name):
    db = SessionLocal()
    try:
        return check_sanctions(db, name)
    finally:
        db.close()


def test_known_sanctioned_name_is_flagged():
    assert _check("Vladimir Putin")["requires_manual_review"] is True


def test_result_is_json_serializable():
    # Regression test for the Week 4 bug: raw UUID objects broke JSONB storage.
    json.dumps(_check("Vladimir Putin"))


def test_ordinary_name_is_not_flagged():
    assert _check("Acme Manufacturing Ltd")["requires_manual_review"] is False