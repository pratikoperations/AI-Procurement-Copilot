"""Focused governed tests for C3.5 Steel scenarios and allocation."""

import copy

import pandas as pd
import pytest

from modules.data_loader import get_demo_data, get_steel_demo_suppliers
from modules.steel_risk import score_and_recommend_steel_suppliers
from modules.steel_scenario import (
    STEEL_SCENARIOS,
    build_steel_allocations,
    calculate_optimized_steel_allocation,
    calculate_standard_steel_allocation,
    run_governed_steel_scenarios,
)

PROFILE = "PPGI_COIL_Z120"
VOLUME = 1_000_000
FX = 83.0


def suppliers():
    return get_steel_demo_suppliers().copy()


def run(mode="Both", scenario_assumptions=None):
    return run_governed_steel_scenarios(
        suppliers(), PROFILE, VOLUME, FX, display_mode=mode,
        scenario_assumptions=scenario_assumptions,
    )


def scored():
    return score_and_recommend_steel_suppliers(suppliers(), PROFILE, VOLUME, FX)[0]


def test_exactly_seven_scenarios_in_frozen_order():
    summary, details = run()
    assert tuple(summary["Scenario"]) == STEEL_SCENARIOS
    assert summary.attrs["scenario_count"] == 7
    assert tuple(details) == STEEL_SCENARIOS


def test_steel_index_scenario_changes_base_steel_only():
    _, details = run()
    base = details["Base Case"]["should_cost"]["components"]
    stressed = details["Steel Index +20%"]["should_cost"]["components"]
    assert stressed["Base Steel"] == pytest.approx(base["Base Steel"] * 1.20)
    for name in ("Controlled Profile / Grade Premium", "Rolling / Conversion Premium", "Zinc Coating", "Paint / Treatment", "Energy Surcharge", "Slitting / Cutting", "Packing", "Freight"):
        assert stressed[name] == pytest.approx(base[name])


def test_energy_conversion_scenario_changes_only_governed_inputs():
    _, details = run()
    base = details["Base Case"]["should_cost"]["components"]
    stressed = details["Energy and Conversion Premium +15%"]["should_cost"]["components"]
    assert stressed["Rolling / Conversion Premium"] == pytest.approx(base["Rolling / Conversion Premium"] * 1.15)
    assert stressed["Energy Surcharge"] == pytest.approx(base["Energy Surcharge"] * 1.15)
    for name in ("Base Steel", "Controlled Profile / Grade Premium", "Zinc Coating", "Paint / Treatment", "Slitting / Cutting", "Packing", "Freight"):
        assert stressed[name] == pytest.approx(base[name])


def test_fx_and_duty_stress_are_disclosed_separately():
    _, details = run()
    stress = details["Import Duty and FX Stress"]
    assert stress["fx_change_pct"] == 10.0
    assert stress["duty_change_pct"] == 10.0
    assert stress["should_cost"]["usd_inr_fx_rate"] == pytest.approx(FX * 1.10)
    assert stress["should_cost"]["import_duty_pct"] == 10.0


def test_domestic_suppliers_do_not_receive_import_duty():
    _, details = run()
    evidence = {row["supplier"]: row for row in details["Import Duty and FX Stress"]["supplier_duty_evidence"]}
    assert evidence["Bharat Steelworks Ltd"]["sourcing_route"] == "Domestic"
    assert evidence["Bharat Steelworks Ltd"]["duty_pct_applied"] == 0.0
    assert evidence["PrimeCoated Metals"]["duty_pct_applied"] == 0.0
    assert evidence["Global Coil Trading"]["sourcing_route"] == "Import"
    assert evidence["Global Coil Trading"]["duty_pct_applied"] == 10.0


def test_demand_stress_recalculates_volume_and_annual_values():
    _, details = run()
    demand = details["Demand +25%"]
    assert demand["should_cost"]["annual_volume_kg"] == 1_250_000
    assert demand["should_cost"]["annual_value_usd"] == pytest.approx(
        demand["should_cost"]["unit_cost_usd_per_kg"] * 1_250_000
    )
    assert demand["optimized_allocation"].attrs["annual_volume_kg"] == 1_250_000


def test_mill_capacity_stress_changes_governed_winner():
    _, details = run()
    assert details["Base Case"]["recommendation"]["winner"] == "Bharat Steelworks Ltd"
    assert details["Mill Allocation and Capacity Stress"]["recommendation"]["winner"] == "PrimeCoated Metals"


def test_mill_capacity_stress_can_produce_no_winner():
    factors = {name: 0.10 for name in suppliers()["Supplier"]}
    _, details = run(scenario_assumptions={"capacity_stress_factors": factors})
    recommendation = details["Mill Allocation and Capacity Stress"]["recommendation"]
    assert recommendation["winner"] is None
    assert recommendation["winner_state"] == "No winner — no technically eligible supplier"


@pytest.mark.parametrize("status,expected_eligible", [
    ("Approved", 2),
    ("Conditional", 0),
    ("Pending", 0),
    ("Rejected", 0),
    ("Non-applicable", 2),
])
def test_grade_substitution_states(status, expected_eligible):
    _, details = run(scenario_assumptions={"grade_substitution_status": status})
    scenario = details["Grade-Substitution Scenario"]
    assert int(scenario["scored_suppliers"]["technical_eligible"].sum()) == expected_eligible
    assert scenario["engineering_approval_provided"] is False


def test_standard_allocation_is_separate_equal_share_output():
    allocation = calculate_standard_steel_allocation(scored(), VOLUME, FX)
    eligible = allocation[allocation["Technical Eligible"]]
    assert allocation.attrs["allocation_type"] == "Standard Allocation"
    assert eligible["Allocated Volume kg"].tolist() == pytest.approx([500_000, 500_000])


def test_optimized_allocation_follows_governed_rank():
    allocation = calculate_optimized_steel_allocation(scored(), VOLUME, FX)
    amounts = dict(zip(allocation["Supplier"], allocation["Allocated Volume kg"]))
    assert allocation.attrs["allocation_type"] == "Optimized Allocation"
    assert amounts["Bharat Steelworks Ltd"] == 1_000_000
    assert amounts["PrimeCoated Metals"] == 0


def test_capacity_constrained_allocation_has_explicit_unallocated_volume():
    limits = {"Bharat Steelworks Ltd": 300_000, "PrimeCoated Metals": 400_000, "Global Coil Trading": 2_000_000}
    allocations = build_steel_allocations(scored(), VOLUME, FX, limits)
    assert allocations["optimized"].attrs["allocated_volume_kg"] == 700_000
    assert allocations["optimized"].attrs["unallocated_volume_kg"] == 300_000
    assert allocations["allocation_state"] == "Partially allocated"


def test_ineligible_supplier_always_receives_zero_allocation():
    allocations = build_steel_allocations(scored(), VOLUME, FX)
    for frame in (allocations["standard"], allocations["optimized"]):
        global_row = frame.loc[frame["Supplier"] == "Global Coil Trading"].iloc[0]
        assert global_row["Technical Eligible"] is False or global_row["Technical Eligible"] == False
        assert global_row["Allocated Volume kg"] == 0
        assert global_row["Allocation %"] == 0


def test_allocation_never_exceeds_demand_or_100_percent():
    allocations = build_steel_allocations(scored(), VOLUME, FX)
    for frame in (allocations["standard"], allocations["optimized"]):
        assert frame["Allocated Volume kg"].sum() <= VOLUME
        assert frame.attrs["total_allocation_pct"] <= 100.0


def test_allocated_volume_never_exceeds_controlled_capacity():
    limits = {"Bharat Steelworks Ltd": 250_000, "PrimeCoated Metals": 350_000, "Global Coil Trading": 0}
    allocation = calculate_optimized_steel_allocation(scored(), VOLUME, FX, limits)
    amounts = dict(zip(allocation["Supplier"], allocation["Allocated Volume kg"]))
    assert amounts["Bharat Steelworks Ltd"] <= 250_000
    assert amounts["PrimeCoated Metals"] <= 350_000


def test_annual_usd_and_inr_values_reconcile():
    allocation = calculate_standard_steel_allocation(scored(), VOLUME, FX)
    for _, row in allocation.iterrows():
        assert row["Annual Value USD"] == pytest.approx(row["Allocated Volume kg"] * row["Normalized USD/kg"])
        assert row["Annual Value INR"] == pytest.approx(row["Annual Value USD"] * FX)


def test_no_eligible_supplier_has_no_winner_and_all_volume_unallocated():
    frame = suppliers()
    frame["Application Approval"] = "Pending"
    rejected, recommendation = score_and_recommend_steel_suppliers(frame, PROFILE, VOLUME, FX)
    allocations = build_steel_allocations(rejected, VOLUME, FX)
    assert recommendation["winner"] is None
    assert allocations["allocation_state"] == "No winner — no technically eligible supplier"
    assert allocations["optimized"].attrs["unallocated_volume_kg"] == VOLUME


def test_risk_cannot_make_ineligible_supplier_allocatable():
    frame = suppliers()
    index = frame.index[frame["Supplier"] == "Global Coil Trading"][0]
    frame.at[index, "Risk Category"] = "Low"
    frame.at[index, "OTIF %"] = 100
    frame.at[index, "Audit Score"] = 100
    frame.at[index, "Quality Continuity Score"] = 100
    scored_frame, _ = score_and_recommend_steel_suppliers(frame, PROFILE, VOLUME, FX)
    allocation = calculate_optimized_steel_allocation(scored_frame, VOLUME, FX)
    assert allocation.loc[allocation["Supplier"] == "Global Coil Trading", "Allocated Volume kg"].item() == 0


def test_display_mode_does_not_change_winner_scenario_or_allocation():
    results = [run(mode) for mode in ("USD", "INR", "Both")]
    summaries = [item[0] for item in results]
    assert summaries[0]["Winner"].tolist() == summaries[1]["Winner"].tolist() == summaries[2]["Winner"].tolist()
    assert summaries[0]["Allocated Volume kg"].tolist() == summaries[1]["Allocated Volume kg"].tolist() == summaries[2]["Allocated Volume kg"].tolist()
    assert summaries[0]["Unallocated Volume kg"].tolist() == summaries[1]["Unallocated Volume kg"].tolist() == summaries[2]["Unallocated Volume kg"].tolist()


def test_normalized_usd_remains_governed_allocation_value_path():
    allocation = calculate_optimized_steel_allocation(scored(), VOLUME, FX)
    assert "Normalized USD/kg" in allocation.columns
    assert "Equivalent INR/kg" in allocation.columns
    assert allocation.attrs["calculation_currency"] == "USD"


def test_invalid_capacity_override_fails_closed():
    with pytest.raises(ValueError):
        calculate_optimized_steel_allocation(scored(), VOLUME, FX, {"Bharat Steelworks Ltd": -1})


def test_non_steel_routes_remain_available():
    assert not get_demo_data("Raw Material Procurement", "PET Resin").empty
    assert not get_demo_data("Raw Material Procurement", "Kraft Paper").empty
    assert not get_demo_data("Packaging Procurement", "Corrugated Board").empty
    assert not get_demo_data("Packaging Procurement", "Flexible Laminates", selected_structure="PET / PE").empty
