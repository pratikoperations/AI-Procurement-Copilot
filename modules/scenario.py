"""Scenario stress testing engine."""

import pandas as pd

from modules.recommendation import recommendation_confidence
from modules.scenario_engine import run_all_flexible_laminate_scenarios
from modules.scoring import enrich_supplier_scores


def _flexible_laminate_scenario_table(base_df, assumptions):
    rows = []
    for result in run_all_flexible_laminate_scenarios(base_df, assumptions):
        winner = result["winner"]
        if winner is None:
            rows.append({
                "Scenario": result["scenario"],
                "Winning Supplier": "No technically eligible supplier",
                "Winning Score": None,
                "Risk-Adjusted TCO per kg (USD)": None,
                "Annual TCO (USD)": None,
                "Risk Resilience Score": None,
                "Failure Probability": None,
                "Technical Eligibility": "No eligible supplier",
                "Standard Allocation Status": "No allocation",
                "Optimized Allocation Status": "No allocation",
                "Scenario Applicable": result["metadata"]["applicable"],
                "Confidence": "Low",
            })
            continue

        rows.append({
            "Scenario": result["scenario"],
            "Winning Supplier": winner["Supplier"],
            "Winning Score": winner["total_score"],
            "Risk-Adjusted TCO per kg (USD)": winner["adjusted_tco_unit_usd"],
            "Annual TCO (USD)": winner["annual_tco_usd"],
            "Risk Resilience Score": winner["risk_score"],
            "Failure Probability": winner["failure_probability"],
            "Technical Eligibility": "Eligible",
            "Standard Allocation Status": (
                "Allocated" if not result["standard_allocation_df"].empty else "No allocation"
            ),
            "Optimized Allocation Status": (
                "Allocated"
                if not result["optimized_allocation"]["allocation_df"].empty
                else "No allocation"
            ),
            "Scenario Applicable": result["metadata"]["applicable"],
            "Confidence": recommendation_confidence(result["scored_df"]),
        })
    return pd.DataFrame(rows)


def run_scenario_table(base_df, assumptions):
    """Run category-aware procurement stress scenarios and return governed winners."""
    if (
        assumptions.get("category") == "Packaging Procurement"
        and assumptions.get("commodity") == "Flexible Laminates"
    ):
        return _flexible_laminate_scenario_table(base_df, assumptions)

    is_kraft = (
        assumptions.get("category") == "Raw Material Procurement"
        and assumptions.get("commodity") == "Kraft Paper"
    )
    material_label = "Paper Price +20%" if is_kraft else "Raw Material +20%"
    scenarios = [
        {"Scenario": "Base Case", "raw_material_shock": 0.0, "freight_shock": 0.0, "demand_change": 0.0},
        {"Scenario": material_label, "raw_material_shock": 0.20, "freight_shock": 0.0, "demand_change": 0.0},
        {"Scenario": "Freight +50%", "raw_material_shock": 0.0, "freight_shock": 0.50, "demand_change": 0.0},
        {"Scenario": "Demand -25%", "raw_material_shock": 0.0, "freight_shock": 0.0, "demand_change": -0.25},
        {"Scenario": "Combined Stress", "raw_material_shock": 0.20, "freight_shock": 0.50, "demand_change": -0.20},
    ]
    if is_kraft:
        scenarios.append({
            "Scenario": "Mill / Fibre Continuity Stress",
            "raw_material_shock": 0.10,
            "freight_shock": 0.10,
            "demand_change": 0.0,
            "kraft_continuity_stress": True,
        })

    rows = []
    unit = str(assumptions.get("category_profile", {}).get("unit", assumptions.get("unit", "unit")))
    if assumptions.get("category") == "Raw Material Procurement":
        unit = str(assumptions.get("category_profile", {}).get("unit", "kg"))

    for scenario in scenarios:
        scenario_assumptions = assumptions.copy()
        scenario_assumptions.update({
            "raw_material_shock": scenario["raw_material_shock"],
            "freight_shock": scenario["freight_shock"],
            "demand_change": scenario["demand_change"],
        })
        scenario_df = base_df.copy()
        if scenario.get("kraft_continuity_stress"):
            scenario_df["Mill Allocation %"] = (scenario_df["Mill Allocation %"] + 8).clip(upper=100)
            scenario_df["Fibre Availability %"] = (scenario_df["Fibre Availability %"] - 15).clip(lower=0)
            scenario_df["Quality Continuity Score"] = (scenario_df["Quality Continuity Score"] - 10).clip(lower=0)

        scored = enrich_supplier_scores(scenario_df, scenario_assumptions)
        winner = scored.iloc[0]
        rows.append({
            "Scenario": scenario["Scenario"],
            "Winning Supplier": winner["Supplier"],
            "Winning Score": winner["total_score"],
            f"Risk-Adjusted TCO per {unit} (USD)": winner["adjusted_tco_unit_usd"],
            "Annual TCO (USD)": winner["annual_tco_usd"],
            "Risk Resilience Score": winner["risk_score"],
            "Failure Probability": winner["failure_probability"],
            "Confidence": recommendation_confidence(scored),
        })
    return pd.DataFrame(rows)
