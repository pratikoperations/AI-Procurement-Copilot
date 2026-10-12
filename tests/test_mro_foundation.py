"""MRO-0 governed foundation regression tests."""

from pathlib import Path

from modules.category_engine import (
    ensure_category_profile,
    get_category_profile,
    get_supported_categories,
    is_production_ready,
)
from modules.commodity_library import get_commodities, get_commodity_profile
from modules.mro_engine import (
    CATEGORY_NAME,
    COMMERCIAL_CONTRACT,
    ENGINE_STATUS,
    EVIDENCE_CONTRACT,
    FIRST_COMMODITY,
    RISK_DIMENSIONS,
    SOURCE_STATUSES,
    SUPPLIER_DATA_CONTRACT,
    TECHNICAL_CONTRACT,
    evaluate_technical_compatibility,
    get_synthetic_demo_suppliers,
)


REQUIREMENT = {
    "bearing_type": "Deep Groove Ball Bearing",
    "bore_diameter_mm": 25,
    "outside_diameter_mm": 52,
    "width_mm": 15,
    "seal_or_shield": "2RS",
    "clearance_class": "C3",
}


def test_mro_category_is_registered_as_foundation_preview_only():
    assert CATEGORY_NAME in get_supported_categories()
    assert FIRST_COMMODITY in get_commodities(CATEGORY_NAME)

    profile = ensure_category_profile(get_category_profile(CATEGORY_NAME, FIRST_COMMODITY))
    assert profile["engine_status"] == ENGINE_STATUS == "Foundation Preview"
    assert profile["selected_commodity"] == "Industrial Bearings"
    assert is_production_ready(CATEGORY_NAME) is False

    # Explicit empty values prevent Packaging defaults leaking into MRO-0.
    assert profile["default_weightings"] == {}
    assert profile["default_assumptions"] == {}
    assert profile["allocation_model"] == "Not enabled in MRO-0"
    assert profile["cost_model"] == "No MRO should-cost model in MRO-0"


def test_industrial_bearings_metadata_models_identity_and_source_status():
    profile = get_commodity_profile(CATEGORY_NAME, FIRST_COMMODITY)
    assert profile["identity_fields"] == ["manufacturer", "manufacturer_part_number"]
    assert profile["source_statuses"] == list(SOURCE_STATUSES)
    assert profile["unit"] == "piece"
    assert profile["source_label"].startswith("Controlled synthetic MRO-0")
    assert profile["required_technical_fields"] == list(TECHNICAL_CONTRACT["required_compatibility_fields"])


def test_mro_contracts_are_explicit_and_do_not_contain_numeric_risk_weights():
    assert TECHNICAL_CONTRACT["required_identity_fields"] == (
        "manufacturer",
        "manufacturer_part_number",
    )
    assert "unit_price" in COMMERCIAL_CONTRACT["required_fields"]
    assert "evidence_status" in EVIDENCE_CONTRACT["required_fields"]
    assert SUPPLIER_DATA_CONTRACT["human_approval_required"] is True
    assert "Approved Equivalent" in SUPPLIER_DATA_CONTRACT["source_statuses"]
    assert len(RISK_DIMENSIONS) >= 6
    assert all(isinstance(item, str) and item for item in RISK_DIMENSIONS)

    profile = get_category_profile(CATEGORY_NAME, FIRST_COMMODITY)
    assert profile["default_weightings"] == {}


def test_technical_compatibility_fails_closed_when_evidence_is_missing():
    offer = dict(REQUIREMENT)
    offer.pop("clearance_class")

    result = evaluate_technical_compatibility(
        REQUIREMENT,
        offer,
        source_status="Authorized Distributor",
    )

    assert result["compatible"] is False
    assert result["status"] == "INSUFFICIENT_EVIDENCE"
    assert result["human_approval_required"] is True


def test_technical_compatibility_fails_closed_on_mismatch():
    offer = dict(REQUIREMENT)
    offer["bore_diameter_mm"] = 30

    result = evaluate_technical_compatibility(
        REQUIREMENT,
        offer,
        source_status="OEM",
    )

    assert result["compatible"] is False
    assert result["status"] == "INCOMPATIBLE"
    assert any("bore_diameter_mm" in reason for reason in result["reasons"])


def test_approved_equivalent_requires_explicit_human_substitution_approval():
    pending = evaluate_technical_compatibility(
        REQUIREMENT,
        REQUIREMENT,
        source_status="Approved Equivalent",
        substitution_approval_status="Human Review Required",
    )
    assert pending["compatible"] is False
    assert pending["status"] == "HUMAN_APPROVAL_REQUIRED"

    approved = evaluate_technical_compatibility(
        REQUIREMENT,
        REQUIREMENT,
        source_status="Approved Equivalent",
        substitution_approval_status="Human Approved",
    )
    assert approved["compatible"] is True
    assert approved["status"] == "COMPATIBLE_FOR_HUMAN_REVIEW"
    assert approved["human_approval_required"] is True


def test_synthetic_supplier_examples_preserve_identity_provenance_and_human_governance():
    suppliers = get_synthetic_demo_suppliers()
    assert suppliers
    for supplier in suppliers:
        assert supplier["manufacturer"]
        assert supplier["manufacturer_part_number"]
        assert supplier["source_status"] in SOURCE_STATUSES
        assert supplier["evidence"]
        for evidence in supplier["evidence"]:
            assert evidence["evidence_status"] == "Synthetic Demonstration"
            assert evidence["manufacturer"] == supplier["manufacturer"]
            assert evidence["manufacturer_part_number"] == supplier["manufacturer_part_number"]


def test_foundation_preview_stops_before_analytical_engines_and_allocation_controls():
    app_source = Path("app.py").read_text(encoding="utf-8")
    sidebar_source = Path("modules/sidebar.py").read_text(encoding="utf-8")

    assert 'if profile["engine_status"] != "Active":' in app_source
    assert "scoring, should-cost" in app_source
    assert "st.stop()" in app_source
    assert 'is_active_category = category_profile["engine_status"] == "Active"' in sidebar_source
    assert "enabled=is_active_category and not is_steel" in sidebar_source
