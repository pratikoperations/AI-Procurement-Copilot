"""Governed C3.7 Steel export production.

Exports are generated only from the selected governed Steel scenario bundle.
They preserve separate USD and INR numeric fields, normalize non-finite values
to JSON null, and never represent an autonomous award or engineering approval.
"""

from __future__ import annotations

from io import BytesIO
import json
import math
from typing import Mapping

import pandas as pd

STEEL_EXCEL_SHEETS = (
    "Supplier Scores Report",
    "Supplier Comparison",
    "Should Cost",
    "Allocation",
    "Standard Allocation",
    "Optimized Allocation",
    "Scenarios",
    "Audit Supplier Scores",
    "C3 Governance",
)


def normalize_strict_steel_json(value):
    """Recursively convert pandas/NumPy missing and non-finite values to null."""
    if value is None:
        return None
    if isinstance(value, pd.DataFrame):
        return normalize_strict_steel_json(value.to_dict(orient="records"))
    if isinstance(value, pd.Series):
        return normalize_strict_steel_json(value.to_list())
    if isinstance(value, Mapping):
        return {str(key): normalize_strict_steel_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [normalize_strict_steel_json(item) for item in value]
    if isinstance(value, (str, bool, int)):
        return value
    if hasattr(value, "item"):
        try:
            value = value.item()
        except (TypeError, ValueError):
            pass
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


def _should_cost_frame(should_cost: Mapping) -> pd.DataFrame:
    components = should_cost.get("components", {})
    rows = []
    for component, unit_usd in components.items():
        unit_value = float(unit_usd)
        rows.append({
            "Component": component,
            "Unit Cost USD/kg": unit_value,
            "Unit Cost INR/kg": unit_value * float(should_cost["usd_inr_fx"]),
            "Annual Value USD": unit_value * float(should_cost["annual_volume_kg"]),
            "Annual Value INR": unit_value * float(should_cost["annual_volume_kg"]) * float(should_cost["usd_inr_fx"]),
        })
    return pd.DataFrame(rows)


def build_steel_governance_manifest(
    state: Mapping,
    summary: pd.DataFrame,
    selected_detail: Mapping,
    usd_inr_fx: float,
    display_mode: str,
) -> dict:
    """Build the strict, screen-reconcilable governed Steel manifest."""
    scored = selected_detail["scored_suppliers"]
    recommendation = selected_detail["recommendation"]
    standard = selected_detail["standard_allocation"]
    optimized = selected_detail["optimized_allocation"]
    should_cost = selected_detail["should_cost"]
    eligible = scored[scored["technical_eligible"].astype(bool)]
    manifest = {
        "contract_version": "C3.7-STEEL-v1",
        "selected_profile": state["steel_profile"],
        "selected_scenario": state["steel_scenario"],
        "annual_volume_kg": float(should_cost["annual_volume_kg"]),
        "annual_volume_metric_tonnes": float(should_cost["annual_volume_kg"]) / 1000.0,
        "usd_inr_fx_assumption": float(usd_inr_fx),
        "fx_source_label": "User-controlled synthetic demonstration assumption; not live FX data.",
        "display_mode": display_mode,
        "calculation_currency": "USD",
        "comparison_unit": "USD/kg",
        "eligible_supplier_count": int(len(eligible)),
        "winner": recommendation.get("winner"),
        "winner_state": recommendation["winner_state"],
        "human_approval_required": True,
        "autonomous_award": False,
        "engineering_approval_provided": False,
        "synthetic_data_boundary": True,
        "live_market_data_claim": False,
        "supplier_scores": scored.to_dict(orient="records"),
        "standard_allocation": standard.to_dict(orient="records"),
        "optimized_allocation": optimized.to_dict(orient="records"),
        "standard_unallocated_volume_kg": float(standard.attrs["unallocated_volume_kg"]),
        "optimized_unallocated_volume_kg": float(optimized.attrs["unallocated_volume_kg"]),
        "scenarios": summary.to_dict(orient="records"),
        "should_cost": dict(should_cost),
        "governance_disclaimer": (
            "Controlled synthetic demonstration only; not metallurgical certification, engineering approval, "
            "mill-certificate authentication, live market intelligence, autonomous award, production allocation, "
            "or realised-savings evidence."
        ),
    }
    return normalize_strict_steel_json({"steel_governance": manifest})


def build_steel_json_export(manifest: Mapping) -> bytes:
    return json.dumps(
        normalize_strict_steel_json(manifest),
        indent=2,
        default=str,
        allow_nan=False,
    ).encode("utf-8")


def build_steel_excel_workbook(
    state: Mapping,
    summary: pd.DataFrame,
    selected_detail: Mapping,
    manifest: Mapping,
) -> bytes:
    """Create the exact nine-sheet governed Steel workbook."""
    scored = selected_detail["scored_suppliers"].copy()
    standard = selected_detail["standard_allocation"].copy()
    optimized = selected_detail["optimized_allocation"].copy()
    should_cost = _should_cost_frame(selected_detail["should_cost"])
    score_columns = [
        "Supplier", "technical_eligible", "normalized_usd_per_kg", "equivalent_inr_per_kg",
        "generic_risk_score", "steel_risk_score", "governed_total_score", "governed_rank",
        "eligibility_failure_reasons",
    ]
    scores = scored[[column for column in score_columns if column in scored.columns]].copy()
    scores = scores.rename(columns={
        "technical_eligible": "Technical Eligibility",
        "normalized_usd_per_kg": "Normalized USD/kg",
        "equivalent_inr_per_kg": "Equivalent INR/kg",
        "generic_risk_score": "Generic Supplier Risk",
        "steel_risk_score": "Steel-Specific Risk",
        "governed_total_score": "Governed Total Score",
        "governed_rank": "Governed Rank",
        "eligibility_failure_reasons": "Eligibility Failure Reasons",
    })
    comparison = scores.copy()
    allocation = optimized.copy()
    governance = pd.DataFrame([
        {"Field": key, "Value": json.dumps(value, default=str, allow_nan=False) if isinstance(value, (dict, list)) else value}
        for key, value in manifest["steel_governance"].items()
        if key not in {"supplier_scores", "standard_allocation", "optimized_allocation", "scenarios", "should_cost"}
    ])
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        scores.to_excel(writer, sheet_name="Supplier Scores Report", index=False)
        comparison.to_excel(writer, sheet_name="Supplier Comparison", index=False)
        should_cost.to_excel(writer, sheet_name="Should Cost", index=False)
        allocation.to_excel(writer, sheet_name="Allocation", index=False)
        standard.to_excel(writer, sheet_name="Standard Allocation", index=False)
        optimized.to_excel(writer, sheet_name="Optimized Allocation", index=False)
        summary.to_excel(writer, sheet_name="Scenarios", index=False)
        scored.to_excel(writer, sheet_name="Audit Supplier Scores", index=False)
        governance.to_excel(writer, sheet_name="C3 Governance", index=False)
    buffer.seek(0)
    return buffer.getvalue()
