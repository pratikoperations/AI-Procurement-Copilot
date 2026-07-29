from __future__ import annotations

from datetime import date
from decimal import Decimal

from modules.ranking_input_semantics import choose_status, field_status, required_fields


def _values():
    return {
        "MEASUREMENT_PERIOD_END_DATE": date(2026, 7, 1),
        "DATA_APPROVAL_STATUS": "APPROVED_SOURCE",
        "AUDIT_DATE": date(2026, 1, 1),
        "AUDIT_STANDARD": "Internal",
        "AUDIT_REFERENCE_ID": "AUD-1",
        "CERTIFICATION_TYPE": "FSC",
        "CERTIFICATION_REFERENCE_ID": "CERT-1",
        "CERTIFICATION_ISSUER": "FSC",
        "CERTIFICATION_VALID_FROM": date(2026, 1, 1),
        "CERTIFICATION_VALID_TO": date(2027, 1, 1),
    }


def test_status_precedence_is_frozen():
    assert choose_status(["MISSING", "STALE", "OUT_OF_RANGE"]) == "OUT_OF_RANGE"
    assert choose_status(["UNVERIFIED", "CONTRADICTORY"]) == "CONTRADICTORY"


def test_valid_and_adversarial_field_statuses():
    status, findings = field_status("OTIF_PERCENT", Decimal("95"), _values(), "SOURCE_MAPPED", date(2026, 7, 29))
    assert status == "VALID" and not findings
    status, findings = field_status("OTIF_PERCENT", Decimal("105"), _values(), "SOURCE_MAPPED", date(2026, 7, 29))
    assert status == "OUT_OF_RANGE" and "RANKING_INPUT_OUT_OF_RANGE" in findings
    status, findings = field_status("OTIF_PERCENT", Decimal("0.95"), _values(), "SOURCE_MAPPED", date(2026, 7, 29), ambiguous_scale=True)
    assert status == "AMBIGUOUS_SCALE" and "RANKING_INPUT_SCALE_AMBIGUOUS" in findings


def test_source_origin_and_evidence_do_not_self_validate():
    values = _values()
    values["DATA_APPROVAL_STATUS"] = "UNVERIFIED"
    status, findings = field_status("SUPPLIER_AUDIT_SCORE", 90, values, None, date(2026, 7, 29))
    assert status == "UNVERIFIED"
    assert "RANKING_VALUE_ORIGIN_MISSING" in findings
    assert "RANKING_SOURCE_UNVERIFIED" in findings


def test_mode_required_sets_are_stable():
    assert len(required_fields("QUICK_RFQ")) == 5
    assert len(required_fields("FULL_SOURCING_REVIEW")) == 10
