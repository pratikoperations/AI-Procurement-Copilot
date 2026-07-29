from __future__ import annotations

from datetime import date
from types import SimpleNamespace

from modules.ranking_input_matching import calculate_mode_eligibility, cross_row_findings, match_ranking_records
from modules.ranking_input_models import CanonicalFieldEvidenceResult, CanonicalRankingRecord, RANKING_FIELDS
from modules.rfq_workbook_adapter import Finding


def _provenance(row, row_id):
    return SimpleNamespace(
        sheet="SUPPLIER_RANKING_INPUTS", source_row_number=row, source_row_id=row_id,
        source_filename="c2.xlsx", source_file_hash_sha256="a" * 64,
        upload_file_hash_sha256="b" * 64, schema_version="1.3.1", alias_registry_version="1.3.1",
    )


def _record(record_id, scope, *, supplier="S1", material="PACK", plant=None, version=1,
            start=date(2026, 1, 1), end=date(2026, 6, 30), row_valid=True, otif=95):
    values = {
        "RANKING_INPUT_RECORD_ID": record_id, "RANKING_INPUT_VERSION": version,
        "SUPPLIER_ID": supplier, "PURCHASING_ORG": "1000", "RANKING_SCOPE": scope,
        "MATERIAL_GROUP": material if scope in {"MATERIAL_GROUP", "PLANT_MATERIAL_GROUP"} else None,
        "PLANT": plant if scope == "PLANT_MATERIAL_GROUP" else None,
        "MEASUREMENT_PERIOD_START_DATE": start, "MEASUREMENT_PERIOD_END_DATE": end,
        "OTIF_PERCENT": otif,
    }
    return CanonicalRankingRecord(values, {"OTIF_PERCENT": "SOURCE_MAPPED"}, None, _provenance(version + 1, record_id), row_valid, True)


def _quote(plant=None):
    values = {
        "RFQ_NUMBER": "RFQ1", "RFQ_ITEM": "10", "SUPPLIER_ID": "S1",
        "PURCHASING_ORG": "1000", "MATERIAL_GROUP": "PACK", "PLANT": plant,
    }
    return SimpleNamespace(canonical_values=values, active=True, eligible_for_analysis=True)


def _evidence(record_id, statuses=None, all_fields=False):
    statuses = statuses or {}
    fields = RANKING_FIELDS if all_fields else (
        "OTIF_PERCENT", "QUALITY_PPM", "SUPPLIER_AUDIT_SCORE", "RECYCLABILITY_PERCENT", "CERTIFICATION_SCORE"
    )
    return tuple(
        CanonicalFieldEvidenceResult(record_id, "S1", field, 90, statuses.get(field, "VALID"), "SOURCE_MAPPED", {}, ())
        for field in fields
    )


def test_scope_matching_prefers_most_specific_record():
    records = (_record("GLOBAL", "SUPPLIER_GLOBAL"), _record("MG", "MATERIAL_GROUP"))
    match = match_ranking_records((_quote(),), records, _evidence("GLOBAL") + _evidence("MG"))[0]
    assert match.ranking_record_id == "MG"
    assert match.matched_scope == "MATERIAL_GROUP"


def test_mode_eligibility_is_per_supplier_item_and_populates_findings():
    match = match_ranking_records((_quote(),), (_record("MG", "MATERIAL_GROUP"),), _evidence("MG"), Finding)[0]
    complete = calculate_mode_eligibility("QUICK_RFQ", (match,), _evidence("MG"), Finding)[0]
    stale_finding = Finding("Blocking", "PERFORMANCE_INPUT_STALE", "stale", "SUPPLIER_RANKING_INPUTS", 2, "QUALITY_PPM")
    evidence = tuple(
        replace.validation_findings and replace or CanonicalFieldEvidenceResult(
            replace.ranking_record_id, replace.supplier_id, replace.canonical_field,
            replace.canonical_value, "STALE", replace.value_origin, replace.source_reference,
            (stale_finding,),
        ) if replace.canonical_field == "QUALITY_PPM" else replace
        for replace in _evidence("MG")
    )
    incomplete = calculate_mode_eligibility("QUICK_RFQ", (match,), evidence, Finding)[0]
    assert complete.status == "RANKING_REVIEW_COMPLETE"
    assert incomplete.status == "RANKING_EVIDENCE_INVALID"
    assert incomplete.invalid_fields == ("QUALITY_PPM",)
    assert incomplete.blocking_findings


def test_quick_optional_invalid_does_not_block_but_full_review_does():
    match = match_ranking_records((_quote(),), (_record("MG", "MATERIAL_GROUP"),), _evidence("MG", all_fields=True))[0]
    evidence = _evidence("MG", {"CARBON_SCORE": "STALE"}, all_fields=True)
    quick = calculate_mode_eligibility("QUICK_RFQ", (match,), evidence)[0]
    full = calculate_mode_eligibility("FULL_SOURCING_REVIEW", (match,), evidence)[0]
    assert quick.status == "RANKING_REVIEW_COMPLETE"
    assert "CARBON_SCORE" not in quick.invalid_fields
    assert full.status == "RANKING_EVIDENCE_INVALID"
    assert "CARBON_SCORE" in full.invalid_fields


def test_cross_row_contradiction_uses_effective_key_not_record_id():
    first = _record("R1", "MATERIAL_GROUP", otif=95)
    second = _record("R2", "MATERIAL_GROUP", otif=90)
    codes = [item.code for item in cross_row_findings((first, second), Finding)]
    assert "CONTRADICTORY_RANKING_INPUT" in codes


def test_equal_highest_version_conflict_is_not_silently_selected():
    first = _record("R1", "MATERIAL_GROUP", version=2, otif=95)
    second = _record("R2", "MATERIAL_GROUP", version=2, otif=90)
    match = match_ranking_records((_quote(),), (first, second), _evidence("R1") + _evidence("R2"), Finding)[0]
    assert match.ranking_record_id is None
    assert match.reason == "RANKING_INPUT_VERSION_CONFLICT"
    assert match.blocking_findings


def test_invalid_higher_version_uses_valid_lower_version():
    lower = _record("LOW", "MATERIAL_GROUP", version=1, row_valid=True)
    higher = _record("HIGH", "MATERIAL_GROUP", version=2, row_valid=False)
    match = match_ranking_records((_quote(),), (lower, higher), _evidence("LOW") + _evidence("HIGH"))[0]
    assert match.ranking_record_id == "LOW"
    assert match.reason == "MATCHED"


def test_invalid_specific_scope_preserves_broader_fallback_but_blocks():
    specific = _record("SPECIFIC", "MATERIAL_GROUP", row_valid=False)
    broader = _record("GLOBAL", "SUPPLIER_GLOBAL", row_valid=True)
    match = match_ranking_records((_quote(),), (specific, broader), _evidence("SPECIFIC") + _evidence("GLOBAL"), Finding)[0]
    assert match.ranking_record_id == "SPECIFIC"
    assert match.fallback_record_id == "GLOBAL"
    assert not match.eligible
    assert match.reason == "SPECIFIC_RANKING_SCOPE_INVALID_FALLBACK_USED"
