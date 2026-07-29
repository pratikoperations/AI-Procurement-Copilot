import json
from pathlib import Path

SCHEMA_PATH = Path("planning/v1.3/build_group_b2/minimum_workbook_schema_v1.3.1.json")
FROZEN_PATH = Path("planning/v1.3/build_group_b/minimum_workbook_schema_v1.3.0.json")


def schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_schema_is_additive_v131_with_fourth_sheet():
    contract = schema()
    assert contract["version"] == "1.3.1"
    assert "SUPPLIER_RANKING_INPUTS" in contract["properties"]
    assert FROZEN_PATH.exists()
    assert json.loads(FROZEN_PATH.read_text(encoding="utf-8"))["version"] == "1.3.0"


def test_all_ranking_fields_are_typed_and_mode_governed():
    contract = schema()
    props = contract["$defs"]["SupplierRankingInputRow"]["properties"]
    fields = {
        "OTIF_PERCENT", "QUALITY_PPM", "SUPPLIER_AUDIT_SCORE",
        "COMPLAINT_RATE_PERCENT", "CAPACITY_BUFFER_PERCENT",
        "RECYCLABILITY_PERCENT", "CERTIFICATION_SCORE", "CARBON_SCORE",
        "EPR_READINESS_SCORE", "PCR_CONTENT_PERCENT",
    }
    assert fields <= set(props)
    assert set(contract["x-mode-requirements"]["FULL_SOURCING_REVIEW"]) == fields
    assert set(contract["x-mode-requirements"]["QUICK_RFQ"]) == {
        "OTIF_PERCENT", "QUALITY_PPM", "SUPPLIER_AUDIT_SCORE",
        "RECYCLABILITY_PERCENT", "CERTIFICATION_SCORE",
    }


def test_percentage_contract_is_zero_to_one_hundred_without_silent_conversion():
    contract = schema()
    assert contract["x-percentage-scale"] == "0_TO_100_ONLY"
    percent = contract["$defs"]["percent"]
    assert percent["minimum"] == 0 and percent["maximum"] == 100
    assert contract["x-migration"]["silent_upgrade"] is False


def test_value_origins_and_evidence_statuses_are_closed():
    contract = schema()
    assert contract["$defs"]["valueOrigin"]["enum"] == [
        "SOURCE_MAPPED", "USER_CONFIRMED", "DERIVED_FROM_HISTORY", "REFERENCE_ENRICHED"
    ]
    assert set(contract["$defs"]["evidenceStatus"]["enum"]) == {
        "VALID", "MISSING", "INVALID_TYPE", "OUT_OF_RANGE", "STALE",
        "AMBIGUOUS_SCOPE", "AMBIGUOUS_SCALE", "CONTRADICTORY", "UNVERIFIED",
    }


def test_scope_and_cross_row_rules_are_explicit():
    contract = schema()
    rules = contract["x-cross-row-rules"]
    assert rules["scope_precedence"] == [
        "PLANT_MATERIAL_GROUP", "MATERIAL_GROUP", "PURCHASING_ORG", "SUPPLIER_GLOBAL"
    ]
    assert "contradictory_duplicate_fatal" in rules["duplicate_policy"]
    row = contract["$defs"]["SupplierRankingInputRow"]
    assert row["additionalProperties"] is False
