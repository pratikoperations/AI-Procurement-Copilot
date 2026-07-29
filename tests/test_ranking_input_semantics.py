from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from modules.ranking_input_models import CanonicalRankingRecord
from modules.ranking_input_semantics import (
    analyze_scale_ambiguity,
    choose_status,
    field_status,
    generate_evidence_results,
    required_fields,
)
from modules.rfq_workbook_adapter import Finding


def _values():
    return {
        "MEASUREMENT_PERIOD_START_DATE": date(2026, 1, 1),
        "MEASUREMENT_PERIOD_END_DATE": date(2026, 7, 1),
        "PERFORMANCE_RECORD_COUNT": 20,
        "DATA_APPROVAL_STATUS": "APPROVED_SOURCE",
        "SOURCE_FILE_NAME": "scorecard.xlsx",
        "SOURCE_ROW_ID": "ROW-1",
        "SOURCE_SYSTEM": "SAP",
        "SOURCE_TRANSACTION_OR_REPORT": "SUPPLIER_SCORECARD",
        "AUDIT_DATE": date(2026, 1, 1),
        "AUDIT_STANDARD": "Internal",
        "AUDIT_REFERENCE_ID": "AUD-1",
        "CERTIFICATION_TYPE": "FSC",
        "CERTIFICATION_REFERENCE_ID": "CERT-1",
        "CERTIFICATION_ISSUER": "FSC",
        "CERTIFICATION_VALID_FROM": date(2026, 1, 1),
        "CERTIFICATION_VALID_TO": date(2027, 1, 1),
    }


def _record(record_id: str, value: Decimal, origin: str = "SOURCE_MAPPED"):
    values = _values() | {
        "RANKING_INPUT_RECORD_ID": record_id,
        "SUPPLIER_ID": "S1",
        "PURCHASING_ORG": "1000",
        "RANKING_SCOPE": "SUPPLIER_GLOBAL",
        "OTIF_PERCENT": value,
    }
    provenance = SimpleNamespace(
        source_row_id=record_id, source_row_number=2, sheet="SUPPLIER_RANKING_INPUTS",
        source_filename="scorecard.xlsx", source_file_hash_sha256="a" * 64,
        upload_file_hash_sha256="b" * 64, schema_version="1.3.1", alias_registry_version="1.3.1",
    )
    return CanonicalRankingRecord(values, {"OTIF_PERCENT": origin}, None, provenance)


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


def test_scale_analysis_detects_fractional_and_mixed_columns():
    assert analyze_scale_ambiguity((_record("R1", Decimal("0.95")),)) == {"OTIF_PERCENT"}
    assert analyze_scale_ambiguity((_record("R1", Decimal("0.95")), _record("R2", Decimal("95")))) == {"OTIF_PERCENT"}


def test_source_origin_and_evidence_do_not_self_validate():
    values = _values(); values["DATA_APPROVAL_STATUS"] = "UNVERIFIED"
    status, findings = field_status("SUPPLIER_AUDIT_SCORE", 90, values, None, date(2026, 7, 29))
    assert status == "UNVERIFIED"
    assert "RANKING_VALUE_ORIGIN_MISSING" in findings
    assert "RANKING_SOURCE_UNVERIFIED" in findings


def test_engine_default_origin_is_dedicated_fatal_finding():
    status, codes = field_status("OTIF_PERCENT", 95, _values(), "DEFAULTED_BY_ENGINE", date(2026, 7, 29))
    assert status == "CONTRADICTORY"
    assert "ENGINE_DEFAULT_ORIGIN_PROHIBITED" in codes
    result = generate_evidence_results((_record("R1", Decimal("95"), "DEFAULTED_BY_ENGINE"),), date(2026, 7, 29), Finding)
    finding = next(item for item in result[0].validation_findings if item.code == "ENGINE_DEFAULT_ORIGIN_PROHIBITED")
    assert finding.severity == "Fatal"


def test_period_and_performance_record_count_are_enforced():
    values = _values(); values["MEASUREMENT_PERIOD_START_DATE"] = date(2026, 8, 1)
    status, codes = field_status("OTIF_PERCENT", 95, values, "SOURCE_MAPPED", date(2026, 7, 29))
    assert status == "UNVERIFIED" and "MEASUREMENT_PERIOD_INVALID" in codes
    values = _values(); values["PERFORMANCE_RECORD_COUNT"] = 0
    status, codes = field_status("OTIF_PERCENT", 95, values, "SOURCE_MAPPED", date(2026, 7, 29))
    assert status == "UNVERIFIED" and "PERFORMANCE_RECORD_COUNT_INVALID" in codes


def test_user_confirmed_origin_requires_matching_confirmation_context():
    status, codes = field_status("OTIF_PERCENT", 95, _values(), "USER_CONFIRMED", date(2026, 7, 29))
    assert status == "UNVERIFIED" and "RANKING_MAPPING_CONFIRMATION_REQUIRED" in codes
    status, codes = field_status("OTIF_PERCENT", 95, _values(), "USER_CONFIRMED", date(2026, 7, 29), confirmed_origins={("OTIF_PERCENT", "USER_CONFIRMED")})
    assert status == "VALID" and not codes


def test_mode_required_sets_are_stable():
    assert len(required_fields("QUICK_RFQ")) == 5
    assert len(required_fields("FULL_SOURCING_REVIEW")) == 10
