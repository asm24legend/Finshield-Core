from services.kyc_features import compute_kyc_features


def test_missing_jurisdiction_is_flagged():
    f = compute_kyc_features("Real Co Ltd", "corporation", None)
    assert f["missing_jurisdiction"] is True


def test_blank_jurisdiction_is_flagged():
    f = compute_kyc_features("Real Co Ltd", "corporation", "   ")
    assert f["missing_jurisdiction"] is True


def test_complete_entity_is_not_flagged():
    f = compute_kyc_features("Real Co Ltd", "corporation", "US-DE")
    assert f["missing_jurisdiction"] is False
    assert f["generic_name_pattern"] is False


def test_generic_name_detected():
    f = compute_kyc_features("Test Corp", "corporation", "US-DE")
    assert f["generic_name_pattern"] is True