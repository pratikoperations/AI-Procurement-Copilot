from __future__ import annotations

from datetime import date
from types import SimpleNamespace

from modules.ranking_input_matching import calculate_mode_eligibility, cross_row_findings, match_ranking_records
from modules.ranking_input_models import CanonicalFieldEvidenceResult, CanonicalRankingRecord
from modules.rfq_workbook_adapter import Finding


def _provenance(row, row_id):
    return SimpleNamespace(
        sheet="SUPPLIER_RANKING_INPUTS", source_row_number=row, source_row_id=row_id,
        source_filename="c2.xlsx", source_file_hash_sha256="a" * 64,
        upload_file_hash_sha256="b" * 64, schema_version="1.3.1", alias_registry_version="1.3.1",
    )


def _record(record_id, scope, *, supplier="S1", material="PACK", plant=None, version=1, start=date(2026, 1, 1), end=date(2026, 6, 30)):
    values = {
        "RANKING_INPUT_RECORD_ID": record_id, "RANKING_INPUT_VERSION": version,
        "SUPPLIER_ID": supplier, "PURCHASING_ORG": "1000", "RANKING_SCOPE": scope,
        "MATERIAL_GROUP": material if scope in {"MATERIAL_GROUP", "PLANT_MATERIAL_GROUP"} else None,
        "PLANT": plant if scope == "PLANT_MATERIAL_GROUP" else None,
        "MEASUREMENT_PERIOD_START_DATE": start, "MEASUREMENT_PERIOD_END_DATE": end,
    }
    return CanonicalRankingRecord(values, {}, None, _provenance(version + 1, record_id), True, True)


def _quote(plant=None):
    values = {
        "RFQ_NUMBER": "RFQ1", "RFQ_ITEM": "10", "SUPPLIER_ID": "S1",
        "PURCHASING_ORG": "1000", "MATERIAL_GROUP": "PACK", "PLANT": plant,
    }
    return SimpleNamespace(canonical_values=values, active=True, eligible_for_analysis=True)


def _evidence(record_id, statuses=None):
    statuses = statuses or {}
    fields = (
        "OTIF_PERCENT", "QUALITY_PPM", "SUPPLIER_AUDIT_SCORE", "RECYCLABILITY_PERCENT", "CERTIFICATION_SCORE"
    )
    return tuple(CanonicalFieldEvidenceResult(record_id, "S1", field, 90, statuses.get(field, "VALID"), "SOURCE_MAPPED", {}, ()) for field in fields)


def test_scope_matching_prefers_most_specific_record():
    records = (_record("GLOBAL", "SUPPLIER_GLOBAL"), _record("MG", "MATERIAL_GROUP"))
    match = match_ranking_records((_quote(),), records, _evidence("GLOBAL") + _evidence("MG"))[0]
    assert match.ranking_record_id == "MG"
    assert match.matched_scope == "MATERIAL_GROUP"


def test_mode_eligibility_is_per_supplier_item():
    match = match_ranking_records((_quote(),), (_record("MG", "MATERIAL_GROUP"),), _evidence("MG"))[0]
    complete = calculate_mode_eligibility("QUICK_RFQ", (match,), _evidence("MG"))[0]
    incomplete = calculate_mode_eligibility("QUICK_RFQ", (match,), _evidence("MG", {"QUALITY_PPM": "STALE"}))[0]
    assert complete.status == "RANKING_REVIEW_COMPLETE"
    assert incomplete.status == "RANKING_EVIDENCE_INVALID"
    assert incomplete.invalid_fields == ("QUALITY_PPM",)


def test_cross_row_duplicate_contradiction_and_overlap_findings():
    exact = _record("R1", "MATERIAL_GROUP")
    duplicate = _record("R1", "MATERIAL_GROUP")
    conflict = _record("R1", "MATERIAL_GROUP", version=2)
    codes = [item.code for item in cross_row_findings((exact, duplicate, conflict), Finding)]
    assert "EXACT_RANKING_INPUT_DUPLICATE" in codes
    assert "CONTRADICTORY_RANKING_INPUT" in codes
    assert "OVERLAPPING_RANKING_MEASUREMENT_PERIOD" in codes
