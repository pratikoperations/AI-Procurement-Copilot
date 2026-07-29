import json
from pathlib import Path

FIXTURE_PATH = Path("tests/fixtures/ranking_input_contract_examples.json")
SCHEMA_PATH = Path("planning/v1.3/build_group_b2/minimum_workbook_schema_v1.3.1.json")
MIGRATION_PATH = Path("planning/v1.3/build_group_b2/RANKING_INPUT_MIGRATION.md")


def fixture():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_valid_quick_example_contains_required_fields_provenance_and_mixed_origins():
    data = fixture()["valid_quick"]
    quick = schema()["x-mode-requirements"]["QUICK_RFQ"]
    assert all(data[field] is not None for field in quick)
    assert set(quick) <= set(data["VALUE_ORIGINS"])
    assert len(set(data["VALUE_ORIGINS"].values())) > 1
    assert len(data["SOURCE_FILE_HASH_SHA256"]) == 64
    assert data["DATA_APPROVAL_STATUS"] == "APPROVED_SOURCE"


def test_full_example_covers_all_ten_fields_and_per_field_origins():
    data = fixture()["valid_full"]
    expected = set(schema()["x-mode-requirements"]["FULL_SOURCING_REVIEW"])
    assert all(data[field] is not None for field in expected)
    assert set(data["VALUE_ORIGINS"]) == expected


def test_adversarial_examples_classify_schema_and_c2_responsibilities():
    cases = {item["case"]: item for item in fixture()["adversarial"]}
    assert cases["fraction_percent"]["value"] == 0.95
    assert cases["fraction_percent"]["enforced_by"] == "BUILD_C2"
    assert cases["over_100"]["enforced_by"] == "JSON_SCHEMA_ENFORCED"
    assert cases["negative_ppm"]["enforced_by"] == "JSON_SCHEMA_ENFORCED"
    assert cases["engine_default"]["value_origin"] == "DEFAULTED_BY_ENGINE"


def test_derived_result_is_per_field_and_not_a_source_assertion():
    result = fixture()["derived_result_example"]
    definition = schema()["$defs"]["CanonicalFieldEvidenceResult"]
    assert set(definition["required"]) <= set(result)
    assert result["canonical_evidence_status"] == "VALID"
    assert schema()["x-derived-adapter-contract"]["computed_by"] == "BUILD_C2"


def test_migration_is_explicit_and_never_silent():
    migration = fixture()["migration"]
    assert migration["v1.3.0"] == "reviewable_but_analytically_blocked"
    assert migration["silent_upgrade"] is False
    text = MIGRATION_PATH.read_text(encoding="utf-8")
    assert "GOVERNED_RANKING_INPUTS_NOT_CANONICAL" in text
    assert "must not" in text
