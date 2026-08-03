"""Scenario stress testing engine."""

import pandas as pd

from modules.hosted_readiness_ui import apply_hosted_readiness_overrides
from modules.multi_supplier_allocation_scenario import run_scenario_allocation
from modules.multi_supplier_allocation_scenario_presenter import build_scenario_presentation
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


def _leading_supplier(scored):
    if scored is None or scored.empty:
        return "", None, None
    row = scored.iloc[0]
    return str(row.get("Supplier", "")), row.get("total_score"), row


def _flexible_laminate_scenario_table(base_df, assumptions):
    rows = []
    for result in run_all_flexible_laminate_scenarios(base_df, assumptions):
        base = _base_row(result)
        supplier, score, leading = _leading_supplier(result["scored_df"])
        presentation = build_scenario_presentation(
            result["scenario_allocation"],
            analytical_leading_supplier=supplier,
            analytical_leading_score=score,
            status_reason=base["Scenario Status / Reason"],
        )
        row = {**base, **presentation.table_row()}
        if not presentation.scenario_applicable:
            row["Winning Supplier"] = "Not applicable"
        elif result["eligible_df"].empty:
            row["Winning Supplier"] = "No technically eligible supplier"
        else:
            row["Winning Supplier"] = supplier
        if leading is None or not presentation.scenario_applicable:
            row.update({
                "Risk-Adjusted TCO per kg (USD)": None,
                "Annual TCO (USD)": None,
                "Risk Resilience Score": None,
                "Failure Probability": None,
                "Technical Eligibility": "Not applicable" if not presentation.scenario_applicable else "Not assessed",
                "Confidence": "Not applicable" if not presentation.scenario_applicable else 0.0,
            })
        else:
            row.update({
                "Risk-Adjusted TCO per kg (USD)": leading.get("adjusted_tco_unit_usd"),
                "Annual TCO (USD)": leading.get("annual_tco_usd"),
                "Risk Resilience Score": leading.get("risk_score"),
                "Failure Probability": leading.get("failure_probability"),
                "Technical Eligibility": "Eligible" if bool(leading.get("technical_eligible", False)) else "Ineligible",
                "Confidence": result["decision"].get(
                    "award_confidence",
                    recommendation_confidence(result["eligible_df"]) if not result["eligible_df"].empty else 0.0,
                ),
            })
        if presentation.blocking_reasons:
            reason = "; ".join(presentation.blocking_reasons)
            row["Scenario Status / Reason"] = reason
            row["Ineligibility / Applicability Reason"] = reason
        rows.append(row)
    return pd.DataFrame(rows)


def _is_steel_route(assumptions):
    return (
        assumptions.get("category") == "Raw Material Procurement"
        and assumptions.get("commodity") == "Steel"
    )


def run_scenario_table(base_df, assumptions):
    """Run category-aware stress scenarios through governed presentation projections.

    Steel remains on its dedicated governed route. Flexible Laminates and generic
    categories expose canonical scenario route status separately from analytical
    supplier ranking; no table row constitutes an autonomous award decision.
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
        scenario_df = base_df.copy(deep=True)
        if scenario.get("kraft_continuity_stress"):
            scenario_df["Mill Allocation %"] = (scenario_df["Mill Allocation %"] + 8).clip(upper=100)
            scenario_df["Fibre Availability %"] = (scenario_df["Fibre Availability %"] - 15).clip(lower=0)
            scenario_df["Quality Continuity Score"] = (scenario_df["Quality Continuity Score"] - 10).clip(lower=0)

        scored = enrich_supplier_scores(scenario_df, scenario_assumptions)
        effective_volume = float(scenario_assumptions["annual_volume"]) * (
            1 + float(scenario_assumptions.get("demand_change", 0.0))
        )
        scenario_allocation = run_scenario_allocation(
            scored,
            scenario_assumptions,
            scenario_name=scenario["Scenario"],
            effective_annual_volume=effective_volume,
            scenario_applicable=True,
            scenario_assumption_version="GENERIC-TABLE-SCENARIO-v1",
            scenario_metadata={
                "scenario": scenario["Scenario"],
                "evidence_origin": "controlled_synthetic",
            },
            evidence_origin="controlled_synthetic",
        )
        supplier, score, leading = _leading_supplier(scored)
        presentation = build_scenario_presentation(
            scenario_allocation,
            analytical_leading_supplier=supplier,
            analytical_leading_score=score,
        )
        row = presentation.table_row()
        row.update({
            "Winning Supplier": supplier,
            f"Risk-Adjusted TCO per {unit} (USD)": leading.get("adjusted_tco_unit_usd") if leading is not None else None,
            "Annual TCO (USD)": leading.get("annual_tco_usd") if leading is not None else None,
            "Risk Resilience Score": leading.get("risk_score") if leading is not None else None,
            "Failure Probability": leading.get("failure_probability") if leading is not None else None,
            "Confidence": recommendation_confidence(scored),
            "Confidence Governance": "Analytical ranking confidence only; human procurement review remains mandatory.",
        })
        rows.append(row)
    return pd.DataFrame(rows)
