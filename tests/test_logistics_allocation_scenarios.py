"""LOGISTICS-3 governed carrier allocation and scenario analysis tests."""

import pytest

from modules.commodity_library import get_commodity_profile
from modules.logistics_allocation import (
    ALLOCATION_SCENARIO_VERSION,
    compare_allocation_scenarios,
    evaluate_allocation_scenario,
    get_allocation_scenario_profile,
)
from modules.logistics_engine import CATEGORY_NAME, FIRST_COMMODITY


CARRIERS = [
    {
        "carrier_id": "LOG-C-001",
        "carrier_name": "Synthetic Carrier A",
        "performance_status": "MEETS_BUYER_POLICY_FOR_HUMAN_REVIEW",
        "landed_freight_inr_per_trip": 24000,
        "available_capacity_trips": 800,
        "proposed_allocation_pct": 60,
        "source_label": "Controlled buyer-reviewed evidence",
    },
    {
        "carrier_id": "LOG-C-002",
        "carrier_name": "Synthetic Carrier B",
        "performance_status": "MEETS_BUYER_POLICY_FOR_HUMAN_REVIEW",
        "landed_freight_inr_per_trip": 26000,
        "available_capacity_trips": 600,
        "proposed_allocation_pct": 40,
        "source_label": "Controlled buyer-reviewed evidence",
    },
]


def test_logistics_3_profile_preserves_human_proposed_allocation_boundary():
    profile = get_allocation_scenario_profile()

    assert profile["contract_version"] == ALLOCATION_SCENARIO_VERSION == "LOGISTICS-3"
    assert profile["engine_status"] == "Foundation Preview"
    assert profile["human_proposed_allocation_required"] is True
    assert profile["carrier_selection_enabled"] is False
    assert profile["carrier_ranking_enabled"] is False
    assert profile["automatic_share_optimization_enabled"] is False
    assert profile["autonomous_award_enabled"] is False
    assert profile["human_approval_required"] is True


def test_commodity_metadata_registers_logistics_3_scenario_contract():
    profile = get_commodity_profile(CATEGORY_NAME, FIRST_COMMODITY)

    assert profile["allocation_scenario_contract_version"] == "LOGISTICS-3"
    assert profile["allocation_scenario_basis"] == "Human-proposed carrier shares"


def test_base_allocation_scenario_reconciles_volume_capacity_and_cost():
    result = evaluate_allocation_scenario(
        annual_trip_demand=1000,
        carriers=CARRIERS,
        scenario_name="Base Case",
    )

    assert result["status"] == "SCENARIO_FEASIBLE_FOR_HUMAN_REVIEW"
    assert result["proposed_allocation_total_pct"] == pytest.approx(100)
    assert result["allocated_trip_total"] == pytest.approx(1000)
    assert result["portfolio_annual_freight_cost_inr"] == pytest.approx(
        600 * 24000 + 400 * 26000
    )
    assert result["weighted_freight_cost_inr_per_trip"] == pytest.approx(24800)
    assert result["blocking_reasons"] == []
    assert result["review_reasons"] == []
    assert all(row["capacity_feasible"] for row in result["allocation_rows"])


def test_demand_stress_recalculates_volume_and_can_expose_capacity_constraint():
    result = evaluate_allocation_scenario(
        annual_trip_demand=1000,
        carriers=CARRIERS,
        scenario_name="Demand +50%",
        demand_change_pct=50,
    )

    assert result["effective_annual_trip_demand"] == pytest.approx(1500)
    assert result["status"] == "SCENARIO_INFEASIBLE"
    assert any("exceeds explicit available capacity" in item for item in result["blocking_reasons"])
    assert result["allocated_trip_total"] == pytest.approx(1500)


def test_unverified_positive_allocation_remains_feasible_but_requires_review():
    carriers = [dict(item) for item in CARRIERS]
    carriers[1]["performance_status"] = "MEETS_POLICY_WITH_UNVERIFIED_EVIDENCE"

    result = evaluate_allocation_scenario(
        annual_trip_demand=1000,
        carriers=carriers,
        scenario_name="Evidence Review",
    )

    assert result["status"] == "SCENARIO_FEASIBLE_WITH_REVIEW"
    assert result["blocking_reasons"] == []
    assert len(result["review_reasons"]) == 1
    assert "unverified performance evidence" in result["review_reasons"][0]


def test_ineligible_carrier_with_positive_share_blocks_scenario():
    carriers = [dict(item) for item in CARRIERS]
    carriers[1]["performance_status"] = "DOES_NOT_MEET_BUYER_POLICY"

    result = evaluate_allocation_scenario(
        annual_trip_demand=1000,
        carriers=carriers,
        scenario_name="Policy Breach",
    )

    assert result["status"] == "SCENARIO_INFEASIBLE"
    assert any("not eligible for positive allocation" in item for item in result["blocking_reasons"])


def test_allocation_must_total_one_hundred_percent():
    carriers = [dict(item) for item in CARRIERS]
    carriers[1]["proposed_allocation_pct"] = 30

    result = evaluate_allocation_scenario(
        annual_trip_demand=1000,
        carriers=carriers,
        scenario_name="Incomplete Allocation",
    )

    assert result["status"] == "SCENARIO_INFEASIBLE"
    assert result["proposed_allocation_total_pct"] == pytest.approx(90)
    assert any("must total 100%" in item for item in result["blocking_reasons"])


@pytest.mark.parametrize(
    ("annual_trip_demand", "demand_change_pct", "message"),
    [
        (0, 0, "greater than zero"),
        (1000, -100, "greater than -100"),
        (1000, float("inf"), "finite"),
    ],
)
def test_invalid_scenario_inputs_fail_closed(annual_trip_demand, demand_change_pct, message):
    with pytest.raises(ValueError, match=message):
        evaluate_allocation_scenario(
            annual_trip_demand=annual_trip_demand,
            carriers=CARRIERS,
            scenario_name="Invalid",
            demand_change_pct=demand_change_pct,
        )


def test_duplicate_carrier_identity_fails_closed():
    carriers = [dict(CARRIERS[0]), dict(CARRIERS[0])]
    carriers[0]["proposed_allocation_pct"] = 50
    carriers[1]["proposed_allocation_pct"] = 50

    with pytest.raises(ValueError, match="Duplicate carrier_id"):
        evaluate_allocation_scenario(
            annual_trip_demand=1000,
            carriers=carriers,
            scenario_name="Duplicate",
        )


def test_compare_scenarios_does_not_select_winner_or_recommend_award():
    base = evaluate_allocation_scenario(
        annual_trip_demand=1000,
        carriers=CARRIERS,
        scenario_name="Base Case",
    )
    stress = evaluate_allocation_scenario(
        annual_trip_demand=1000,
        carriers=CARRIERS,
        scenario_name="Demand +20%",
        demand_change_pct=20,
    )

    result = compare_allocation_scenarios([base, stress])

    assert len(result["scenarios"]) == 2
    assert result["winner_selected"] is False
    assert result["recommendation_created"] is False
    assert result["human_approval_required"] is True


def test_no_selection_ranking_optimization_or_writeback_is_claimed():
    result = evaluate_allocation_scenario(
        annual_trip_demand=1000,
        carriers=CARRIERS,
        scenario_name="Governance",
    )

    assert result["carrier_selection_performed"] is False
    assert result["carrier_ranking_performed"] is False
    assert result["automatic_share_optimization_performed"] is False
    assert result["award_recommendation_created"] is False
    assert result["external_data_used"] is False
    assert result["tms_erp_writeback_performed"] is False
    assert result["human_approval_required"] is True
