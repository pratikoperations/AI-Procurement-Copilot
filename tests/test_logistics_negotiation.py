"""LOGISTICS-4 governed negotiation intelligence and decision presentation tests."""

import pytest

from modules.commodity_library import get_commodity_profile
from modules.logistics_engine import CATEGORY_NAME, FIRST_COMMODITY
from modules.logistics_negotiation import (
    NEGOTIATION_VERSION,
    build_carrier_negotiation_brief,
    build_logistics_decision_summary,
    get_negotiation_profile,
)


CARRIER = {
    "carrier_id": "LOG-C-001",
    "carrier_name": "Synthetic Carrier A",
    "current_landed_freight_inr_per_trip": 25000,
    "annual_allocated_trips": 600,
    "source_label": "Controlled buyer-reviewed commercial evidence",
}

POSITION = {
    "target_freight_inr_per_trip": 23500,
    "commercial_ceiling_inr_per_trip": 24500,
    "target_payment_terms_days": 45,
    "target_detention_free_hours": 4,
    "target_service_commitment": "OTIF >= 96% with agreed recovery plan",
}

SCENARIO = {
    "scenario_name": "Base Case",
    "status": "SCENARIO_FEASIBLE_FOR_HUMAN_REVIEW",
    "effective_annual_trip_demand": 1000,
    "portfolio_annual_freight_cost_inr": 24800000,
    "weighted_freight_cost_inr_per_trip": 24800,
}


def test_logistics_4_profile_preserves_advisory_boundary():
    profile = get_negotiation_profile()

    assert profile["contract_version"] == NEGOTIATION_VERSION == "LOGISTICS-4"
    assert profile["engine_status"] == "Foundation Preview"
    assert profile["autonomous_negotiation_enabled"] is False
    assert profile["commercial_commitment_enabled"] is False
    assert profile["carrier_selection_enabled"] is False
    assert profile["award_recommendation_enabled"] is False
    assert profile["human_approval_required"] is True


def test_commodity_metadata_registers_logistics_4_contract():
    profile = get_commodity_profile(CATEGORY_NAME, FIRST_COMMODITY)

    assert profile["negotiation_contract_version"] == "LOGISTICS-4"
    assert profile["negotiation_target_basis"] == "Explicit buyer-entered positions"


def test_negotiation_brief_calculates_transparent_target_deltas():
    result = build_carrier_negotiation_brief(
        carrier=CARRIER,
        buyer_position=POSITION,
    )

    assert result["price_position"] == "ABOVE_BUYER_CEILING"
    assert result["target_saving_inr_per_trip"] == pytest.approx(1500)
    assert result["annual_target_saving_inr"] == pytest.approx(900000)
    assert result["annual_ceiling_saving_inr"] == pytest.approx(300000)
    assert "Freight rate" in result["negotiation_priorities"]
    assert "Service commitment" in result["negotiation_priorities"]
    assert result["autonomous_negotiation_performed"] is False
    assert result["commercial_commitment_created"] is False
    assert result["award_recommendation_created"] is False


def test_at_or_below_target_has_zero_target_saving():
    carrier = dict(CARRIER)
    carrier["current_landed_freight_inr_per_trip"] = 23000

    result = build_carrier_negotiation_brief(
        carrier=carrier,
        buyer_position=POSITION,
    )

    assert result["price_position"] == "AT_OR_BELOW_TARGET"
    assert result["target_saving_inr_per_trip"] == 0
    assert result["annual_target_saving_inr"] == 0


def test_target_must_not_exceed_commercial_ceiling():
    position = dict(POSITION)
    position["target_freight_inr_per_trip"] = 25000
    position["commercial_ceiling_inr_per_trip"] = 24000

    with pytest.raises(ValueError, match="must not exceed the commercial ceiling"):
        build_carrier_negotiation_brief(
            carrier=CARRIER,
            buyer_position=position,
        )


@pytest.mark.parametrize(
    ("override", "message"),
    [
        ({"target_freight_inr_per_trip": None}, "Missing buyer negotiation position fields"),
        ({"target_payment_terms_days": -1}, "zero or greater"),
        ({"target_detention_free_hours": float("inf")}, "finite"),
        ({"target_service_commitment": " "}, "target_service_commitment is required"),
    ],
)
def test_invalid_buyer_positions_fail_closed(override, message):
    position = {**POSITION, **override}

    with pytest.raises(ValueError, match=message):
        build_carrier_negotiation_brief(
            carrier=CARRIER,
            buyer_position=position,
        )


def test_decision_summary_aggregates_explicit_negotiation_deltas_without_award():
    brief_a = build_carrier_negotiation_brief(
        carrier=CARRIER,
        buyer_position=POSITION,
    )
    carrier_b = {
        **CARRIER,
        "carrier_id": "LOG-C-002",
        "carrier_name": "Synthetic Carrier B",
        "current_landed_freight_inr_per_trip": 26000,
        "annual_allocated_trips": 400,
    }
    position_b = {
        **POSITION,
        "target_freight_inr_per_trip": 25000,
        "commercial_ceiling_inr_per_trip": 25500,
    }
    brief_b = build_carrier_negotiation_brief(
        carrier=carrier_b,
        buyer_position=position_b,
    )

    result = build_logistics_decision_summary(
        scenario_result=SCENARIO,
        negotiation_briefs=[brief_a, brief_b],
    )

    assert result["potential_annual_target_saving_inr"] == pytest.approx(
        900000 + 400000
    )
    assert len(result["carrier_negotiation_summary"]) == 2
    assert result["scenario_winner_selected"] is False
    assert result["carrier_award_selected"] is False
    assert result["commercial_commitment_created"] is False
    assert result["human_approval_required"] is True


def test_decision_summary_requires_governed_scenario_fields():
    scenario = dict(SCENARIO)
    scenario.pop("weighted_freight_cost_inr_per_trip")

    with pytest.raises(ValueError, match="Missing scenario result fields"):
        build_logistics_decision_summary(
            scenario_result=scenario,
            negotiation_briefs=[],
        )
