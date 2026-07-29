import copy
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError
from referencing import Registry, Resource

SCHEMA_PATH = Path("planning/v1.3/build_group_b2/minimum_workbook_schema_v1.3.1.json")
FROZEN_PATH = Path("planning/v1.3/build_group_b/minimum_workbook_schema_v1.3.0.json")
FIXTURE_PATH = Path("tests/fixtures/ranking_input_contract_examples.json")
FROZEN_URN = "urn:aipc:minimum-workbook:1.3.0"


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validator():
    schema = load_json(SCHEMA_PATH)
    frozen = load_json(FROZEN_PATH)
    registry = Registry().with_resource(FROZEN_URN, Resource.from_contents(frozen))
    return Draft202012Validator(schema, registry=registry)


def valid_rfq_row():
    return {
        "SOURCING_EVENT_ID": "EV-1", "RFQ_NUMBER": "RFQ-1", "RFQ_ITEM": "10",
        "QUOTATION_VERSION": 1, "SUPPLIER_ID": "S-1", "SUPPLIER_NAME": "Supplier One",
        "MATERIAL_DESCRIPTION": "Bottle", "MATERIAL_GROUP": "PACK", "PURCHASING_ORG": "1000",
        "REQUESTED_QUANTITY": 1000, "QUOTED_QUANTITY": 1000, "QUOTATION_UOM": "EA",
        "COMPARISON_UOM": "EA", "BASE_UNIT_PRICE": 1.2, "PRICE_UNIT": 1, "CURRENCY": "USD",
        "QUOTATION_DATE": "2026-07-01", "VALIDITY_END_DATE": "2026-12-31",
        "QUOTATION_STATUS": "VALID", "SOURCE_TRANSACTION": "ME47",
        "SOURCE_FILE_NAME": "rfq.xlsx", "SOURCE_EXTRACTED_AT": "2026-07-29T10:00:00",
        "SOURCE_ROW_ID": "RFQ-ROW-1",
    }


def valid_history_row():
    return {
        "PO_NUMBER": "4500000010", "PO_ITEM": "10", "PO_DATE": "2026-06-01",
        "SUPPLIER_ID": "S-1", "SUPPLIER_NAME": "Supplier One",
        "MATERIAL_DESCRIPTION": "Bottle", "MATERIAL_GROUP": "PACK", "PURCHASING_ORG": "1000",
        "ORDER_QUANTITY": 1000, "ORDER_UOM": "EA", "COMPARISON_UOM": "EA",
        "NET_PRICE": 1.1, "PRICE_UNIT": 1, "CURRENCY": "USD", "NET_ORDER_VALUE": 1100,
        "PO_STATUS": "OPEN", "DELETION_FLAG": False, "SOURCE_TRANSACTION": "ME2N",
        "SOURCE_FILE_NAME": "history.xlsx", "SOURCE_EXTRACTED_AT": "2026-07-29T10:00:00",
        "SOURCE_ROW_ID": "PO-ROW-1",
    }


def workbook_with(ranking_row):
    return {
        "RFQ_QUOTES": [valid_rfq_row()],
        "PO_HISTORY": [valid_history_row()],
        "UPLOAD_METADATA": [{}],
        "SUPPLIER_RANKING_INPUTS": [ranking_row],
    }


def test_schema_is_additive_v131_and_resolves_frozen_contract_locally():
    schema = load_json(SCHEMA_PATH)
    frozen = load_json(FROZEN_PATH)
    assert schema["version"] == "1.3.1"
    assert schema["x-local-schema-registry"]["network_resolution"] is False
    assert schema["x-local-schema-registry"]["resources"][FROZEN_URN].endswith("minimum_workbook_schema_v1.3.0.json")
    assert frozen["version"] == "1.3.0"
    validator().validate(workbook_with(load_json(FIXTURE_PATH)["valid_quick"]))


def test_frozen_rfq_history_and_metadata_contracts_remain_enforced():
    candidate = workbook_with(load_json(FIXTURE_PATH)["valid_quick"])
    validator().validate(candidate)
    bad = copy.deepcopy(candidate)
    bad["RFQ_QUOTES"][0]["UNKNOWN_FROZEN_FIELD"] = "x"
    with pytest.raises(ValidationError):
        validator().validate(bad)


def test_valid_full_review_row_passes_executable_schema_validation():
    validator().validate(workbook_with(load_json(FIXTURE_PATH)["valid_full"]))


@pytest.mark.parametrize(
    ("field", "value"),
    [("PCR_CONTENT_PERCENT", 101), ("OTIF_PERCENT", -1), ("QUALITY_PPM", -1)],
)
def test_invalid_numeric_ranges_fail(field, value):
    row = copy.deepcopy(load_json(FIXTURE_PATH)["valid_full"])
    row[field] = value
    with pytest.raises(ValidationError):
        validator().validate(workbook_with(row))


def test_fractional_percentage_is_not_silently_converted():
    row = copy.deepcopy(load_json(FIXTURE_PATH)["valid_quick"])
    row["OTIF_PERCENT"] = 0.95
    validator().validate(workbook_with(row))
    assert row["OTIF_PERCENT"] == 0.95
    assert "semantic percentage-scale ambiguity" in load_json(SCHEMA_PATH)["x-rule-classification"]["BUILD_C2_ENFORCED"]


def test_missing_audit_and_certification_evidence_fail():
    for removed in ("AUDIT_REFERENCE_ID", "CERTIFICATION_REFERENCE_ID"):
        row = copy.deepcopy(load_json(FIXTURE_PATH)["valid_quick"])
        row.pop(removed)
        with pytest.raises(ValidationError):
            validator().validate(workbook_with(row))


def test_invalid_scope_combinations_fail():
    row = copy.deepcopy(load_json(FIXTURE_PATH)["valid_quick"])
    row["RANKING_SCOPE"] = "SUPPLIER_GLOBAL"
    with pytest.raises(ValidationError):
        validator().validate(workbook_with(row))
    row = copy.deepcopy(load_json(FIXTURE_PATH)["valid_quick"])
    row["PLANT"] = "P100"
    with pytest.raises(ValidationError):
        validator().validate(workbook_with(row))


def test_unknown_property_and_invalid_hash_fail():
    for mutation in ("UNKNOWN_FIELD", "BAD_HASH"):
        row = copy.deepcopy(load_json(FIXTURE_PATH)["valid_quick"])
        if mutation == "UNKNOWN_FIELD":
            row[mutation] = "x"
        else:
            row["SOURCE_FILE_HASH_SHA256"] = "not-a-sha"
        with pytest.raises(ValidationError):
            validator().validate(workbook_with(row))


def test_source_status_is_non_authoritative_and_canonical_status_is_derived():
    schema = load_json(SCHEMA_PATH)
    row = schema["$defs"]["SupplierRankingInputRow"]
    assert "EVIDENCE_STATUS" not in row["properties"]
    assert "SOURCE_EVIDENCE_STATUS" in row["properties"]
    assert schema["x-derived-adapter-contract"]["canonical_evidence_status_is_source_input"] is False
    derived = schema["$defs"]["CanonicalFieldEvidenceResult"]
    assert "canonical_evidence_status" in derived["required"]


def test_per_field_origins_and_rule_classification_are_explicit():
    schema = load_json(SCHEMA_PATH)
    origins = schema["$defs"]["SupplierRankingInputRow"]["properties"]["VALUE_ORIGINS"]
    assert origins["additionalProperties"] is False
    assert "OTIF_PERCENT" in origins["properties"]
    assert set(schema["x-rule-classification"]) == {
        "JSON_SCHEMA_ENFORCED", "BUILD_C2_ENFORCED", "DOCUMENTARY_POLICY"
    }
