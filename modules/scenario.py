"""Scenario stress testing engine."""

import pandas as pd

from modules.scoring import enrich_supplier_scores
from modules.recommendation import recommendation_confidence


def run_scenario_table(base_df, assumptions):
    """Run standard procurement stress scenarios and return winning supplier by scenario."""
    scenarios = [
        {"Scenario": "Base Case", "raw_material_shock": 0.0, "freight_shock": 0.0, "demand_change": 0.0},
        {"Scenario": "Raw Material +20%", "raw_material_shock": 0.20, "freight_shock": 0.0, "demand_change": 0.0},
        {"Scenario": "Freight +50%", "raw_material_shock": 0.0, "freight_shock": 0.50, "demand_change": 0.0},
        {"Scenario": "Demand -25%", "raw_material_shock": 0.0, "freight_shock": 0.0, "demand_change": -0.25},
        {"Scenario": "Combined Stress", "raw_material_shock": 0.20, "freight_shock": 0.50, "demand_change": -0.20},
    ]

    rows = []
    for scenario in scenarios:
        scenario_assumptions = assumptions.copy()
        scenario_assumptions.update(
            {
                "raw_material_shock": scenario["raw_material_shock"],
                "freight_shock": scenario["freight_shock"],
                "demand_change": scenario["demand_change"],
            }
        )
        scored = enrich_supplier_scores(base_df, scenario_assumptions)
        winner = scored.iloc[0]
        rows.append(
            {
                "Scenario": scenario["Scenario"],
                "Winning Supplier": winner["Supplier"],
                "Winning Score": winner["total_score"],
                "Advanced TCO Unit USD": winner["adjusted_tco_unit_usd"],
                "Annual TCO USD": winner["annual_tco_usd"],
                "Risk Score": winner["risk_score"],
                "Failure Probability": winner["failure_probability"],
                "Confidence": recommendation_confidence(scored),
            }
        )

    return pd.DataFrame(rows)
