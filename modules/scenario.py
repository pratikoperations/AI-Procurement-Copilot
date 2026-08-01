"""Scenario stress testing engine."""

import pandas as pd

from modules.hosted_readiness_ui import apply_hosted_readiness_overrides
from modules.recommendation import recommendation_confidence
from modules.scenario_engine import run_all_flexible_laminate_scenarios
from modules.scoring import enrich_supplier_scores


def _tooling_status(result):
    metadata = result["metadata"]
    applied = int(metadata.get("replacement_applied_count", 0))
    already_new = int(metadata.get("already_new_tooling_count", 0))
    if result["scenario"] != "Tooling Replacement Scenario":
        return "Applied" if metadata.get("applicable", True) else metadata.get("reason", "Not applicable")
    if applied == 0 and already_new > 0:
        return "No replacement applied — suppliers already use new-tooling economics"
    if applied > 0:
        return f"Replacement applied to {applied} supplier row(s)"
    return "No tooling replacement applicable"


def _base_row(result):
    metadata = result["metadata"]
    status = _tooling_status(result)
    return {
        "Scenario": result["scenario"],
        "Scenario Applicable": bool(metadata["applicable"]),
        "Scenario Status / Reason": status,
        "Ineligibility / Applicability Reason": status,
        "Confidence Governance": result["decision"].get("confidence_governance", ""),
        "Scenario Assumption Version": metadata["scenario_assumption_version"],
        "Tooling Replacement Applied": int(metadata.get("replacement_applied_count", 0)),
        "Already New Tooling": int(metadata.get("already_new_tooling_count", 0)),
        "Tooling Not Applicable": int(metadata.get("not_applicable_count", 0)),
    }


def _flexible_laminate_scenario_table(base_df, assumptions):
    rows = []
    for result in run_all_flexible_laminate_scenarios(base_df, assumptions):
        base = _base_row(result)
        applicable = bool(result["metadata"]["applicable"])
        winner = result["winner"]
        if not applicable:
            rows.append({**base, "Winning Supplier": "Not applicable", "Winning Score": None, "Risk-Adjusted TCO per kg (USD)": None, "Annual TCO (USD)": None, "Risk Resilience Score": None, "Failure Probability": None, "Technical Eligibility": "Not applicable", "Standard Allocation Status": "Not applicable", "Optimized Allocation Status": "Not applicable", "Confidence": "Not applicable"})
            continue
        if winner is None:
            reason = result["ineligibility_reasons"]
            rows.append({**base, "Scenario Status / Reason": reason, "Ineligibility / Applicability Reason": reason, "Winning Supplier": "No technically eligible supplier", "Winning Score": None, "Risk-Adjusted TCO per kg (USD)": None, "Annual TCO (USD)": None, "Risk Resilience Score": None, "Failure Probability": None, "Technical Eligibility": "No eligible supplier", "Standard Allocation Status": "No allocation", "Optimized Allocation Status": "No allocation", "Confidence": 0.0})
            continue
        confidence = result["decision"].get("award_confidence", recommendation_confidence(result["eligible_df"]))
        rows.append({**base, "Winning Supplier": winner["Supplier"], "Winning Score": winner["total_score"], "Risk-Adjusted TCO per kg (USD)": winner["adjusted_tco_unit_usd"], "Annual TCO (USD)": winner["annual_tco_usd"], "Risk Resilience Score": winner["risk_score"], "Failure Probability": winner["failure_probability"], "Technical Eligibility": "Eligible", "Standard Allocation Status": "Allocated" if not result["standard_allocation_df"].empty else "No allocation", "Optimized Allocation Status": "Allocated" if not result["optimized_allocation"]["allocation_df"].empty else "No allocation", "Confidence": confidence})
    return pd.DataFrame(rows)


def _is_steel_route(assumptions):
    return (
        assumptions.get("category") == "Raw Material Procurement"
        and assumptions.get("commodity") == "Steel"
    )


def run_scenario_table(base_df, assumptions):
    """Run category-aware procurement stress scenarios and return governed winners.

    Steel is dispatched to its dedicated governed dashboard before any generic
    scenario, recommendation, allocation or export path can continue. The Steel
    dashboard terminates the Streamlit run after rendering its seven governed
    scenarios and category-specific downloads.
    """
    apply_hosted_readiness_overrides()

    if _is_steel_route(assumptions):
        from modules.steel_ux import render_steel_governed_dashboard

        render_steel_governed_dashboard(base_df, assumptions)
        raise RuntimeError("Steel governed route returned without terminating the Streamlit run.")

    if assumptions.get("category") == "Packaging Procurement" and assumptions.get("commodity") == "Flexible Laminates":
        return _flexible_laminate_scenario_table(base_df, assumptions)
    is_kraft = assumptions.get("category") == "Raw Material Procurement" and assumptions.get("commodity") == "Kraft Paper"
    material_label = "Paper Price +20%" if is_kraft else "Raw Material +20%"
    scenarios = [
        {"Scenario": "Base Case", "raw_material_shock": 0.0, "freight_shock": 0.0, "demand_change": 0.0},
        {"Scenario": material_label, "raw_material_shock": 0.20, "freight_shock": 0.0, "demand_change": 0.0},
        {"Scenario": "Freight +50%", "raw_material_shock": 0.0, "freight_shock": 0.50, "demand_change": 0.0},
        {"Scenario": "Demand -25%", "raw_material_shock": 0.0, "freight_shock": 0.0, "demand_change": -0.25},
        {"Scenario": "Combined Stress", "raw_material_shock": 0.20, "freight_shock": 0.50, "demand_change": -0.20},
    ]
    if is_kraft:
        scenarios.append({"Scenario": "Mill / Fibre Continuity Stress", "raw_material_shock": 0.10, "freight_shock": 0.10, "demand_change": 0.0, "kraft_continuity_stress": True})
    rows = []
    unit = str(assumptions.get("category_profile", {}).get("unit", assumptions.get("unit", "unit")))
    if assumptions.get("category") == "Raw Material Procurement":
        unit = str(assumptions.get("category_profile", {}).get("unit", "kg"))
    for scenario in scenarios:
        scenario_assumptions = assumptions.copy()
        scenario_assumptions.update({"raw_material_shock": scenario["raw_material_shock"], "freight_shock": scenario["freight_shock"], "demand_change": scenario["demand_change"]})
        scenario_df = base_df.copy()
        if scenario.get("kraft_continuity_stress"):
            scenario_df["Mill Allocation %"] = (scenario_df["Mill Allocation %"] + 8).clip(upper=100)
            scenario_df["Fibre Availability %"] = (scenario_df["Fibre Availability %"] - 15).clip(lower=0)
            scenario_df["Quality Continuity Score"] = (scenario_df["Quality Continuity Score"] - 10).clip(lower=0)
        scored = enrich_supplier_scores(scenario_df, scenario_assumptions)
        winner = scored.iloc[0]
        rows.append({"Scenario": scenario["Scenario"], "Winning Supplier": winner["Supplier"], "Winning Score": winner["total_score"], f"Risk-Adjusted TCO per {unit} (USD)": winner["adjusted_tco_unit_usd"], "Annual TCO (USD)": winner["annual_tco_usd"], "Risk Resilience Score": winner["risk_score"], "Failure Probability": winner["failure_probability"], "Confidence": recommendation_confidence(scored)})
    return pd.DataFrame(rows)
