"""LOGISTICS-0 governed foundation regression tests."""

from pathlib import Path

from modules.category_engine import (
    ensure_category_profile,
    get_category_profile,
    get_supported_categories,
    is_production_ready,
)
from modules.commodity_library import get_commodities, get_commodity_profile
from modules.logistics_engine import (
    CARRIER_DATA_CONTRACT,
    CARRIER_STATUSES,
    CATEGORY_NAME,
    COMMERCIAL_CONTRACT,
    ENGINE_STATUS,
    EVIDENCE_CONTRACT,
    FIRST_COMMODITY,
    LANE_SERVICE_CONTRACT,
    PERFORMANCE_CONTRACT,
    RISK_DIMENSIONS,
    evaluate_service_compatibility,
    get_synthetic_demo_carriers,
)


REQUIREMENT = {
    "origin_location": "Pune, Maharashtra",
    "destination_location": "Navi Mumbai, Maharashtra",
    "transport_mode": "Road",
    "service_type": "Full Truck Load",
    "vehicle_type": "Closed Body Truck",
    "minimum_payload_capacity_tonnes": 16,
}


def test_logistics_category_is_registered_as_foundation_preview_only():
    assert CATEGORY_NAME in get_supported_categories()
    assert FIRST_COMMODITY in get_commodities(CATEGORY_NAME)

    profile = ensure_category_profile(get_category_profile(CATEGORY_NAME, FIRST_COMMODITY))
    assert profile["engine_status"] == ENGINE_STATUS == "Foundation Preview"
    assert profile["selected_commodity"] == FIRST_COMMODITY
    assert profile["unit"] == "trip"
    assert is_production_ready(CATEGORY_NAME) is False

    assert profile["default_weightings"] == {}
    assert profile["default_assumptions"] == {}
    assert profile["allocation_model"] == "Not enabled in LOGISTICS-0"
    assert profile["cost_model"] == "No freight-cost calculation model in LOGISTICS-0"


def test_ftl_metadata_models_lane_identity_and_service_requirements():
    profile = get_commodity_profile(CATEGORY_NAME, FIRST_COMMODITY)

    assert profile["identity_fields"] == [
        "origin_location",
        "destination_location",
        "transport_mode",
        "service_type",
    ]
    assert profile["unit"] == "trip"
    assert profile["rate_basis_options"] == ["Per Trip", "Per Tonne", "Per Tonne-Km"]
    assert profile["required_service_fields"] == list(
        LANE_SERVICE_CONTRACT["required_compatibility_fields"]
    )
    assert profile["source_label"].startswith("Controlled synthetic LOGISTICS-0")


def test_logistics_contracts_are_explicit_without_score_weights_or_cost_formula():
    assert "base_freight_rate" in COMMERCIAL_CONTRACT["required_fields"]
    assert "fuel_surcharge_basis" in COMMERCIAL_CONTRACT["required_fields"]
    assert "otif_pct" in PERFORMANCE_CONTRACT["required_fields"]
    assert "evidence_status" in EVIDENCE_CONTRACT["required_fields"]
    assert CARRIER_DATA_CONTRACT["human_approval_required"] is True
    assert "Spot / Unverified Carrier" in CARRIER_DATA_CONTRACT["carrier_statuses"]

    assert len(RISK_DIMENSIONS) >= 6
    assert all(isinstance(item, str) and item for item in RISK_DIMENSIONS)

    profile = get_category_profile(CATEGORY_NAME, FIRST_COMMODITY)
    assert profile["default_weightings"] == {}
    assert "No freight-cost calculation" in profile["cost_model"]


def test_service_compatibility_fails_closed_when_evidence_is_missing():
    offer = dict(REQUIREMENT)
    offer.pop("vehicle_type")

    result = evaluate_service_compatibility(
        REQUIREMENT,
        offer,
        carrier_status="Approved Carrier",
    )

    assert result["compatible"] is False
    assert result["status"] == "INSUFFICIENT_EVIDENCE"
    assert result["human_approval_required"] is True


def test_service_compatibility_fails_closed_on_lane_or_service_mismatch():
    offer = dict(REQUIREMENT)
    offer["destination_location"] = "Different Destination"

    result = evaluate_service_compatibility(
        REQUIREMENT,
        offer,
        carrier_status="Contracted Carrier",
    )

    assert result["compatible"] is False
    assert result["status"] == "INCOMPATIBLE"
    assert any("destination_location" in reason for reason in result["reasons"])


def test_spot_unverified_carrier_requires_explicit_human_approval():
    pending = evaluate_service_compatibility(
        REQUIREMENT,
        REQUIREMENT,
        carrier_status="Spot / Unverified Carrier",
        carrier_approval_status="Human Review Required",
    )
    assert pending["compatible"] is False
    assert pending["status"] == "HUMAN_APPROVAL_REQUIRED"

    approved = evaluate_service_compatibility(
        REQUIREMENT,
        REQUIREMENT,
        carrier_status="Spot / Unverified Carrier",
        carrier_approval_status="Human Approved",
    )
    assert approved["compatible"] is True
    assert approved["status"] == "COMPATIBLE_FOR_HUMAN_REVIEW"
    assert approved["human_approval_required"] is True


def test_synthetic_carrier_examples_preserve_lane_and_evidence_provenance():
    carriers = get_synthetic_demo_carriers()

    assert carriers
    for carrier in carriers:
        assert carrier["carrier_name"]
        assert carrier["carrier_status"] in CARRIER_STATUSES
        assert carrier["lane_service_evidence"]
        assert carrier["commercial_evidence"]
        assert carrier["performance_evidence"]
        assert carrier["evidence"]
        for evidence in carrier["evidence"]:
            assert evidence["evidence_status"] == "Synthetic Demonstration"
            assert evidence["carrier_name"] == carrier["carrier_name"]


def test_foundation_preview_stops_before_analytical_engines_and_allocation_controls():
    app_source = Path("app.py").read_text(encoding="utf-8")
    sidebar_source = Path("modules/sidebar.py").read_text(encoding="utf-8")

    assert 'if profile["engine_status"] != "Active":' in app_source
    assert "scoring, should-cost" in app_source
    assert "st.stop()" in app_source
    assert 'is_active_category = category_profile["engine_status"] == "Active"' in sidebar_source
    assert "enabled=is_active_category and not is_steel" in sidebar_source
