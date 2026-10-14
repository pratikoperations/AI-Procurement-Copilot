"""LOGISTICS-1 governed FTL freight-normalization regression tests."""

import math

import pytest

from modules.commodity_library import get_commodity_profile
from modules.logistics_engine import (
    CATEGORY_NAME,
    FIRST_COMMODITY,
    FREIGHT_NORMALIZATION_CONTRACT,
    FREIGHT_NORMALIZATION_VERSION,
    get_freight_normalization_profile,
    normalize_ftl_freight_quote,
)


COMMON = {
    "payload_tonnes": 16,
    "lane_distance_km": 150,
    "quote_currency": "INR",
    "evidence_status": "Supplied — Unverified",
    "source_label": "Controlled supplier quotation",
}


def test_logistics_1_profile_is_bounded_and_keeps_category_in_foundation_preview():
    profile = get_freight_normalization_profile()

    assert profile["contract_version"] == FREIGHT_NORMALIZATION_VERSION == "LOGISTICS-1"
    assert profile["engine_status"] == "Foundation Preview"
    assert profile["calculation_currency"] == "INR"
    assert profile["comparison_units"] == ("INR/trip", "INR/tonne", "INR/tonne-km")
    assert profile["carrier_scoring_enabled"] is False
    assert profile["scenario_engine_enabled"] is False
    assert profile["allocation_enabled"] is False
    assert profile["route_optimization_enabled"] is False
    assert profile["autonomous_award_enabled"] is False
    assert profile["human_approval_required"] is True


def test_commodity_metadata_registers_logistics_1_comparison_contract():
    profile = get_commodity_profile(CATEGORY_NAME, FIRST_COMMODITY)

    assert profile["freight_normalization_contract_version"] == "LOGISTICS-1"
    assert profile["comparison_units"] == ["INR/trip", "INR/tonne", "INR/tonne-km"]
    assert profile["assumption_profile_version"] == "LOGISTICS-0"


@pytest.mark.parametrize(
    ("rate_basis", "base_rate"),
    [
        ("Per Trip", 24000),
        ("Per Tonne", 1500),
        ("Per Tonne-Km", 10),
    ],
)
def test_rate_bases_normalize_to_same_base_freight_per_trip(rate_basis, base_rate):
    result = normalize_ftl_freight_quote(
        base_freight_rate=base_rate,
        rate_basis=rate_basis,
        **COMMON,
    )

    assert result["normalized_base_freight_inr_per_trip"] == pytest.approx(24000)
    assert result["landed_freight_inr_per_trip"] == pytest.approx(24000)
    assert result["landed_freight_inr_per_tonne"] == pytest.approx(1500)
    assert result["landed_freight_inr_per_tonne_km"] == pytest.approx(10)


def test_landed_freight_reconciles_explicit_fuel_toll_and_accessorial_components():
    result = normalize_ftl_freight_quote(
        base_freight_rate=24000,
        rate_basis="Per Trip",
        fuel_surcharge_treatment="Percent of Base Freight",
        fuel_surcharge_value=10,
        toll_treatment="Fixed Amount Per Trip",
        toll_amount=800,
        detention_amount=500,
        loading_unloading_amount=300,
        other_accessorial_amount=200,
        **COMMON,
    )

    assert result["components_inr_per_trip"] == {
        "Base Freight": 24000.0,
        "Fuel Surcharge": 2400.0,
        "Toll": 800.0,
        "Detention": 500.0,
        "Loading / Unloading": 300.0,
        "Other Accessorial": 200.0,
    }
    assert result["landed_freight_inr_per_trip"] == pytest.approx(28200)
    assert result["landed_freight_inr_per_tonne"] == pytest.approx(1762.5)
    assert result["landed_freight_inr_per_tonne_km"] == pytest.approx(11.75)


def test_fixed_fuel_surcharge_is_not_reinterpreted_as_percentage():
    result = normalize_ftl_freight_quote(
        base_freight_rate=24000,
        rate_basis="Per Trip",
        fuel_surcharge_treatment="Fixed Amount Per Trip",
        fuel_surcharge_value=1200,
        **COMMON,
    )

    assert result["components_inr_per_trip"]["Fuel Surcharge"] == pytest.approx(1200)
    assert result["landed_freight_inr_per_trip"] == pytest.approx(25200)


def test_included_components_reject_conflicting_nonzero_amounts():
    with pytest.raises(ValueError, match="Included fuel surcharge"):
        normalize_ftl_freight_quote(
            base_freight_rate=24000,
            rate_basis="Per Trip",
            fuel_surcharge_treatment="Included",
            fuel_surcharge_value=1,
            **COMMON,
        )

    with pytest.raises(ValueError, match="Included toll treatment"):
        normalize_ftl_freight_quote(
            base_freight_rate=24000,
            rate_basis="Per Trip",
            toll_treatment="Included",
            toll_amount=1,
            **COMMON,
        )


@pytest.mark.parametrize(
    ("override", "message"),
    [
        ({"quote_currency": "USD"}, "INR quotations only"),
        ({"payload_tonnes": 0}, "Payload tonnes must be greater than zero"),
        ({"lane_distance_km": 0}, "Lane distance km must be greater than zero"),
        ({"source_label": " "}, "Source label is required"),
        ({"evidence_status": "Unknown"}, "Unsupported evidence status"),
        ({"rate_basis": "Per Km"}, "Unsupported freight rate basis"),
    ],
)
def test_normalization_fails_closed_on_unsupported_or_missing_governed_inputs(override, message):
    inputs = {
        "base_freight_rate": 24000,
        "rate_basis": "Per Trip",
        **COMMON,
        **override,
    }

    with pytest.raises(ValueError, match=message):
        normalize_ftl_freight_quote(**inputs)


def test_normalization_preserves_provenance_and_no_autonomous_decision_claims():
    result = normalize_ftl_freight_quote(
        base_freight_rate=24000,
        rate_basis="Per Trip",
        **COMMON,
    )

    assert result["contract_version"] == "LOGISTICS-1"
    assert result["evidence_status"] == "Supplied — Unverified"
    assert result["source_label"] == "Controlled supplier quotation"
    assert result["external_data_used"] is False
    assert result["market_benchmark_inferred"] is False
    assert result["carrier_scoring_performed"] is False
    assert result["allocation_performed"] is False
    assert result["route_optimization_performed"] is False
    assert result["award_recommendation_created"] is False
    assert result["human_approval_required"] is True
    assert "base_normalization" in result["calculation_trace"]
    assert "landed_freight" in result["calculation_trace"]


def test_contract_has_no_default_market_rate_or_unsupported_weighting():
    assert FREIGHT_NORMALIZATION_CONTRACT["supported_quote_currencies"] == ("INR",)
    assert "market_rate" not in FREIGHT_NORMALIZATION_CONTRACT
    assert "default_fuel_rate" not in FREIGHT_NORMALIZATION_CONTRACT
    assert "carrier_score_weights" not in FREIGHT_NORMALIZATION_CONTRACT
    assert math.isfinite(1.0)
