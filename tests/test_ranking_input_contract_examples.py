import json
from pathlib import Path

FIXTURE_PATH = Path("tests/fixtures/ranking_input_contract_examples.json")
SCHEMA_PATH = Path("planning/v1.3/build_group_b2/minimum_workbook_schema_v1.3.1.json")
MIGRATION_PATH = Path("planning/v1.3/build_group_b2/RANKING_INPUT_MIGRATION.md")


def fixture():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_valid_quick_example_contains_required_fields_and_provenance():
    data = fixture()["valid_quick"]
    quick = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))["x-mode-requirements"]["QUICK_RFQ"]
    assert all(data[field] is not None for field in quick)
    assert data["OTIF_PERCENT"] == 96.5
    assert 0 <= data["RECYCLABILITY_PERCENT"] <= 100
    assert len(data["SOURCE_FILE_HASH_SHA256"]) == 64
    assert data["DATA_APPROVAL_STATUS"] == "APPROVED_SOURCE"


def test_full_example_covers_all_ten_ranking_fields():
    data = fixture()["valid_full"]
    expected = set(json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))["x-mode-requirements"]["FULL_SOURCING_REVIEW"])
    assert set(data) == expected


def test_adversarial_examples_prohibit_silent_scale_and_engine_defaults():
    cases = {item["case"]: item for item in fixture()["adversarial"]}
    assert cases["fraction_percent"]["value"] == 0.95
    assert cases["fraction_percent"]["expected_status"] == "AMBIGUOUS_SCALE"
    assert cases["over_100"]["expected_status"] == "OUT_OF_RANGE"
    assert cases["negative_ppm"]["expected_status"] == "OUT_OF_RANGE"
    assert cases["engine_default"]["value_origin"] == "DEFAULTED_BY_ENGINE"
    assert cases["engine_default"]["expected_status"] == "UNVERIFIED"


def test_migration_is_explicit_and_never_silent():
    migration = fixture()["migration"]
    assert migration["v1.3.0"] == "reviewable_but_analytically_blocked"
    assert migration["silent_upgrade"] is False
    text = MIGRATION_PATH.read_text(encoding="utf-8")
    assert "GOVERNED_RANKING_INPUTS_NOT_CANONICAL" in text
    assert "must not" in text
