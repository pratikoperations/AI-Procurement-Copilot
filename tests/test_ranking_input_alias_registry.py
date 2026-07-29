import json
from pathlib import Path

REGISTRY_PATH = Path("planning/v1.3/build_group_b2/sap_report_alias_registry_v1.3.1.json")
FROZEN_PATH = Path("planning/v1.3/build_group_b/sap_report_alias_registry_v1.3.0.json")


def registry():
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def test_registry_is_additive_v131_and_frozen_registry_remains_v130():
    data = registry()
    assert data["registry_version"] == "1.3.1"
    assert "SUPPLIER_RANKING_INPUTS" in data["sheets"]
    assert json.loads(FROZEN_PATH.read_text(encoding="utf-8"))["registry_version"] == "1.3.0"


def test_all_ten_ranking_fields_have_narrow_aliases_and_confirmation():
    data = registry()
    aliases = data["sheets"]["SUPPLIER_RANKING_INPUTS"]
    fields = {
        "OTIF_PERCENT", "QUALITY_PPM", "SUPPLIER_AUDIT_SCORE",
        "COMPLAINT_RATE_PERCENT", "CAPACITY_BUFFER_PERCENT",
        "RECYCLABILITY_PERCENT", "CERTIFICATION_SCORE", "CARBON_SCORE",
        "EPR_READINESS_SCORE", "PCR_CONTENT_PERCENT",
    }
    assert fields <= set(aliases)
    assert all(aliases[field] for field in fields)
    rules = data["mapping_rules"]
    assert rules["all_non_canonical_ranking_aliases_require_confirmation"] is True
    assert rules["silent_fraction_to_percent_conversion"] is False
    assert rules["percentage_scale"] == "0_TO_100_ONLY"


def test_confirmation_identity_binds_scale_origin_and_versions():
    identity = set(registry()["mapping_rules"]["confirmation_identity"])
    assert {
        "upload_hash_sha256", "schema_version", "alias_registry_version",
        "sheet", "source_header", "canonical_field", "detected_scale", "value_origin",
    } <= identity


def test_ambiguous_semantic_headers_are_rejected_examples():
    rejected = registry()["rejected_semantic_aliases"]
    for header in (
        "Delivery Performance", "Quality Score", "Supplier Rating", "Certification",
        "Recycled Content %", "Carbon Footprint", "EPR Compliant", "Capacity",
    ):
        assert header in rejected
