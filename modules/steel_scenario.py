"""Governed C3.5 Steel scenarios and allocation.

This module operates only on controlled synthetic demonstration data. It does not
provide live market data, engineering substitution approval, autonomous award,
production allocation, or realised-savings evidence.
"""

from __future__ import annotations

import math
from copy import deepcopy
from typing import Mapping

import pandas as pd

from modules.steel_cost import (
    CONTROLLED_STEEL_COST_ASSUMPTIONS,
    add_steel_currency_values,
    calculate_steel_should_cost,
)
from modules.steel_risk import score_and_recommend_steel_suppliers

STEEL_SCENARIOS = (
    "Base Case",
    "Steel Index +20%",
    "Energy and Conversion Premium +15%",
    "Import Duty and FX Stress",
    "Demand +25%",
    "Mill Allocation and Capacity Stress",
    "Grade-Substitution Scenario",
)

PROFILE_COMPONENT_DEFAULTS = {
    "CR_COIL_COMMERCIAL": (0.0, 0.0),
    "GI_COIL_Z120": (0.08, 0.0),
    "PPGI_COIL_Z120": (0.08, 0.12),
}

DEFAULT_SCENARIO_ASSUMPTIONS = {
    "fx_stress_pct": 10.0,
    "import_duty_stress_pct": 10.0,
    "demand_stress_pct": 25.0,
    "mill_allocation_stress_points": 15.0,
    "capacity_stress_factors": {
        "Bharat Steelworks Ltd": 0.50,
        "PrimeCoated Metals": 1.00,
        "Global Coil Trading": 0.50,
    },
    "grade_substitution_status": "Approved",
}


def _finite(value, label: str, *, positive: bool = False, non_negative: bool = False) -> float:
    if value is None or isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite numeric value.")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} must be a finite numeric value.")
    if positive and result <= 0:
        raise ValueError(f"{label} must be greater than zero.")
    if non_negative and result < 0:
        raise ValueError(f"{label} must be non-negative.")
    return result


def _profile_cost_assumptions(profile_id: str, overrides: Mapping | None = None) -> dict:
    if profile_id not in PROFILE_COMPONENT_DEFAULTS:
        raise ValueError(f"Unsupported Steel profile '{profile_id}'.")
    zinc, paint = PROFILE_COMPONENT_DEFAULTS[profile_id]
    values = dict(CONTROLLED_STEEL_COST_ASSUMPTIONS)
    values.update({"zinc_cost_usd_per_kg": zinc, "paint_treatment_usd_per_kg": paint})
    if overrides:
        values.update(overrides)
    return values


def _should_cost(profile_id: str, volume: float, fx: float, display_mode: str, assumptions: Mapping) -> dict:
    result = calculate_steel_should_cost(
        profile_id=profile_id,
        annual_volume_kg=volume,
        base_steel_usd_per_kg=assumptions["base_steel_usd_per_kg"],
        profile_premium_usd_per_kg=assumptions["profile_premium_usd_per_kg"],
        rolling_conversion_usd_per_kg=assumptions["rolling_conversion_usd_per_kg"],
        zinc_cost_usd_per_kg=assumptions["zinc_cost_usd_per_kg"],
        paint_treatment_usd_per_kg=assumptions["paint_treatment_usd_per_kg"],
        energy_surcharge_usd_per_kg=assumptions["energy_surcharge_usd_per_kg"],
        yield_pct=assumptions["yield_pct"],
        slitting_cutting_usd_per_kg=assumptions["slitting_cutting_usd_per_kg"],
        packing_usd_per_kg=assumptions["packing_usd_per_kg"],
        freight_usd_per_kg=assumptions["freight_usd_per_kg"],
        sourcing_route=assumptions["sourcing_route"],
        import_duty_pct=assumptions["import_duty_pct"],
        supplier_margin_pct=assumptions["supplier_margin_pct"],
    )
    return add_steel_currency_values(result, fx, display_mode)


def _capacity_map(scored: pd.DataFrame, overrides: Mapping | None = None) -> dict[str, float]:
    capacities = {}
    for _, row in scored.iterrows():
        capacity = _finite(row["Supplier Capacity"], f"Supplier Capacity for {row['Supplier']}", non_negative=True)
        if overrides and row["Supplier"] in overrides:
            capacity = _finite(overrides[row["Supplier"]], f"Capacity override for {row['Supplier']}", non_negative=True)
        capacities[str(row["Supplier"])] = capacity
    return capacities


def _allocation_frame(scored: pd.DataFrame, volumes: Mapping[str, float], annual_volume_kg: float, fx: float, label: str) -> pd.DataFrame:
    rows = []
    for _, supplier in scored.iterrows():
        name = str(supplier["Supplier"])
        volume = float(volumes.get(name, 0.0)) if bool(supplier["technical_eligible"]) else 0.0
        unit_usd = float(supplier["normalized_usd_per_kg"])
        rows.append({
            "Supplier": name,
            "Allocation Type": label,
            "Technical Eligible": bool(supplier["technical_eligible"]),
            "Allocated Volume kg": volume,
            "Allocation %": volume / annual_volume_kg * 100.0,
            "Normalized USD/kg": unit_usd,
            "Equivalent INR/kg": unit_usd * fx,
            "Annual Value USD": volume * unit_usd,
            "Annual Value INR": volume * unit_usd * fx,
            "Supplier Capacity kg": float(supplier["Supplier Capacity"]),
        })
    frame = pd.DataFrame(rows)
    allocated = float(frame["Allocated Volume kg"].sum()) if not frame.empty else 0.0
    frame.attrs.update({
        "allocation_type": label,
        "annual_volume_kg": annual_volume_kg,
        "allocated_volume_kg": allocated,
        "unallocated_volume_kg": max(0.0, annual_volume_kg - allocated),
        "total_allocation_pct": allocated / annual_volume_kg * 100.0,
        "calculation_currency": "USD",
        "display_currency_invariant": True,
    })
    if allocated > annual_volume_kg + 1e-9 or frame.attrs["total_allocation_pct"] > 100.0 + 1e-9:
        raise ValueError("Steel allocation exceeds governed annual demand.")
    return frame


def calculate_standard_steel_allocation(
    scored: pd.DataFrame,
    annual_volume_kg: float,
    usd_inr_fx: float,
    capacity_overrides: Mapping | None = None,
) -> pd.DataFrame:
    """Capacity-constrained equal-share allocation across eligible suppliers."""
    volume = _finite(annual_volume_kg, "Annual volume", positive=True)
    fx = _finite(usd_inr_fx, "USD/INR FX", positive=True)
    capacities = _capacity_map(scored, capacity_overrides)
    eligible = [str(row["Supplier"]) for _, row in scored.iterrows() if bool(row["technical_eligible"])]
    allocations = {name: 0.0 for name in scored["Supplier"].astype(str)}
    remaining = volume
    active = list(eligible)
    while active and remaining > 1e-9:
        equal_share = remaining / len(active)
        next_active = []
        progress = 0.0
        for name in active:
            available = max(0.0, capacities[name] - allocations[name])
            amount = min(equal_share, available)
            allocations[name] += amount
            progress += amount
            if available - amount > 1e-9:
                next_active.append(name)
        remaining -= progress
        if progress <= 1e-9:
            break
        active = next_active
    return _allocation_frame(scored, allocations, volume, fx, "Standard Allocation")


def calculate_optimized_steel_allocation(
    scored: pd.DataFrame,
    annual_volume_kg: float,
    usd_inr_fx: float,
    capacity_overrides: Mapping | None = None,
) -> pd.DataFrame:
    """Fill eligible suppliers by governed rank without exceeding capacity."""
    volume = _finite(annual_volume_kg, "Annual volume", positive=True)
    fx = _finite(usd_inr_fx, "USD/INR FX", positive=True)
    capacities = _capacity_map(scored, capacity_overrides)
    allocations = {name: 0.0 for name in scored["Supplier"].astype(str)}
    remaining = volume
    ordered = scored.sort_values("governed_rank")
    for _, row in ordered.iterrows():
        if remaining <= 1e-9:
            break
        if not bool(row["technical_eligible"]):
            continue
        name = str(row["Supplier"])
        amount = min(remaining, capacities[name])
        allocations[name] = amount
        remaining -= amount
    return _allocation_frame(scored, allocations, volume, fx, "Optimized Allocation")


def build_steel_allocations(
    scored: pd.DataFrame,
    annual_volume_kg: float,
    usd_inr_fx: float,
    capacity_overrides: Mapping | None = None,
) -> dict:
    standard = calculate_standard_steel_allocation(scored, annual_volume_kg, usd_inr_fx, capacity_overrides)
    optimized = calculate_optimized_steel_allocation(scored, annual_volume_kg, usd_inr_fx, capacity_overrides)
    state = "Allocated" if optimized.attrs["unallocated_volume_kg"] <= 1e-9 else "Partially allocated"
    if int(scored["technical_eligible"].sum()) == 0:
        state = "No winner — no technically eligible supplier"
    return {"standard": standard, "optimized": optimized, "allocation_state": state}


def _supplier_duty_evidence(scored: pd.DataFrame, duty_pct: float) -> list[dict]:
    evidence = []
    for _, row in scored.iterrows():
        route = "Import" if float(row["Import Dependency %"]) > 50.0 else "Domestic"
        evidence.append({
            "supplier": row["Supplier"],
            "sourcing_route": route,
            "duty_pct_applied": duty_pct if route == "Import" else 0.0,
        })
    return evidence


def run_governed_steel_scenarios(
    suppliers: pd.DataFrame,
    profile_id: str,
    annual_volume_kg: float,
    usd_inr_fx: float,
    display_mode: str = "Both",
    cost_assumptions: Mapping | None = None,
    risk_assumptions: Mapping | None = None,
    scenario_assumptions: Mapping | None = None,
) -> tuple[pd.DataFrame, dict[str, dict]]:
    """Execute exactly seven governed scenarios in frozen order."""
    volume = _finite(annual_volume_kg, "Annual volume", positive=True)
    fx = _finite(usd_inr_fx, "USD/INR FX", positive=True)
    controlled = deepcopy(DEFAULT_SCENARIO_ASSUMPTIONS)
    if scenario_assumptions:
        controlled.update(scenario_assumptions)
    base_cost = _profile_cost_assumptions(profile_id, cost_assumptions)
    details: dict[str, dict] = {}

    def evaluate(name: str, scenario_suppliers: pd.DataFrame, scenario_volume: float, scenario_fx: float,
                 assumptions: Mapping, substitution_status: str = "Not applicable",
                 substitution_requested: bool = False, capacity_overrides: Mapping | None = None) -> None:
        scored, recommendation = score_and_recommend_steel_suppliers(
            scenario_suppliers, profile_id, scenario_volume, scenario_fx, display_mode,
            risk_assumptions, substitution_status, substitution_requested,
        )
        allocation = build_steel_allocations(scored, scenario_volume, scenario_fx, capacity_overrides)
        cost = _should_cost(profile_id, scenario_volume, scenario_fx, display_mode, assumptions)
        details[name] = {
            "scored_suppliers": scored,
            "recommendation": recommendation,
            "standard_allocation": allocation["standard"],
            "optimized_allocation": allocation["optimized"],
            "allocation_state": allocation["allocation_state"],
            "should_cost": cost,
        }

    evaluate("Base Case", suppliers.copy(), volume, fx, base_cost)

    index_cost = dict(base_cost)
    index_cost["base_steel_usd_per_kg"] *= 1.20
    evaluate("Steel Index +20%", suppliers.copy(), volume, fx, index_cost)

    energy_cost = dict(base_cost)
    energy_cost["rolling_conversion_usd_per_kg"] *= 1.15
    energy_cost["energy_surcharge_usd_per_kg"] *= 1.15
    evaluate("Energy and Conversion Premium +15%", suppliers.copy(), volume, fx, energy_cost)

    stressed_fx = fx * (1.0 + _finite(controlled["fx_stress_pct"], "FX stress %", non_negative=True) / 100.0)
    duty_pct = _finite(controlled["import_duty_stress_pct"], "Import duty stress %", non_negative=True)
    import_cost = dict(base_cost)
    import_cost.update({"sourcing_route": "Import", "import_duty_pct": duty_pct})
    evaluate("Import Duty and FX Stress", suppliers.copy(), volume, stressed_fx, import_cost)
    details["Import Duty and FX Stress"]["fx_change_pct"] = controlled["fx_stress_pct"]
    details["Import Duty and FX Stress"]["duty_change_pct"] = duty_pct
    details["Import Duty and FX Stress"]["supplier_duty_evidence"] = _supplier_duty_evidence(
        details["Import Duty and FX Stress"]["scored_suppliers"], duty_pct
    )

    demand_volume = volume * (1.0 + _finite(controlled["demand_stress_pct"], "Demand stress %", non_negative=True) / 100.0)
    evaluate("Demand +25%", suppliers.copy(), demand_volume, fx, base_cost)

    stressed_suppliers = suppliers.copy()
    factors = controlled["capacity_stress_factors"]
    capacity_overrides = {}
    for index, row in stressed_suppliers.iterrows():
        factor = _finite(factors.get(row["Supplier"], 1.0), f"Capacity stress factor for {row['Supplier']}", non_negative=True)
        capacity = float(row["Supplier Capacity"]) * factor
        stressed_suppliers.at[index, "Supplier Capacity"] = capacity
        stressed_suppliers.at[index, "Mill Allocation %"] = min(
            100.0,
            float(row["Mill Allocation %"]) + _finite(controlled["mill_allocation_stress_points"], "Mill allocation stress", non_negative=True),
        )
        capacity_overrides[str(row["Supplier"])] = capacity
    evaluate("Mill Allocation and Capacity Stress", stressed_suppliers, volume, fx, base_cost, capacity_overrides=capacity_overrides)

    substitution_status = str(controlled["grade_substitution_status"])
    requested = substitution_status.casefold() != "non-applicable"
    normalized_status = "Not applicable" if substitution_status.casefold() == "non-applicable" else substitution_status
    evaluate("Grade-Substitution Scenario", suppliers.copy(), volume, fx, base_cost, normalized_status, requested)
    details["Grade-Substitution Scenario"]["engineering_approval_provided"] = False
    details["Grade-Substitution Scenario"]["substitution_status"] = normalized_status

    rows = []
    for name in STEEL_SCENARIOS:
        detail = details[name]
        recommendation = detail["recommendation"]
        optimized = detail["optimized_allocation"]
        cost = detail["should_cost"]
        rows.append({
            "Scenario": name,
            "Scenario Status": "Evaluated",
            "Winner": recommendation.get("winner"),
            "Winner State": recommendation["winner_state"],
            "Annual Volume kg": float(cost["annual_volume_kg"]),
            "Unit Cost USD/kg": float(cost["unit_cost_usd_per_kg"]),
            "Unit Cost INR/kg": float(cost["unit_cost_inr_per_kg"]),
            "Annual Value USD": float(cost["annual_value_usd"]),
            "Annual Value INR": float(cost["annual_value_inr"]),
            "Allocated Volume kg": float(optimized.attrs["allocated_volume_kg"]),
            "Unallocated Volume kg": float(optimized.attrs["unallocated_volume_kg"]),
            "Allocation State": detail["allocation_state"],
            "Human Approval Required": True,
            "Engineering Approval Provided": False,
        })
    summary = pd.DataFrame(rows)
    summary.attrs.update({
        "scenario_count": len(summary),
        "scenario_order": STEEL_SCENARIOS,
        "calculation_currency": "USD",
        "display_mode": display_mode,
        "assumption_boundary": "Controlled synthetic scenario assumptions; not live market data or engineering approval.",
    })
    return summary, details
