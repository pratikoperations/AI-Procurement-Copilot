"""Deterministic supplier allocation optimizer for executive sourcing decisions."""

import pandas as pd

SUPPORTED_SPLITS = [(100, 0), (90, 10), (80, 20), (70, 30), (60, 40), (50, 50)]


def optimize_allocation(scored_df, annual_volume):
    """Recommend a two-supplier allocation using score gap, risk, performance, and capacity."""
    if scored_df.empty:
        return {"allocation_df": pd.DataFrame(), "explanation": "No suppliers available for allocation."}

    primary = scored_df.iloc[0]
    if len(scored_df) == 1:
        allocation = pd.DataFrame([
            {"Supplier": primary["Supplier"], "Recommended Allocation %": 100.0, "Role": "Primary Supplier"}
        ])
        return {
            "allocation_df": allocation,
            "explanation": "100/0 allocation because only one supplier is available; continuity mitigation is required.",
        }

    secondary = scored_df.iloc[1]
    gap = float(primary["total_score"] - secondary["total_score"])
    primary_capacity = float(primary.get("Supplier Capacity", annual_volume))
    primary_capacity_share = min(primary_capacity / max(float(annual_volume), 1.0) * 100, 100)
    primary_risk = float(primary["risk_score"])
    primary_performance = float(primary["performance_score"])

    if primary_capacity_share < 60 or primary_risk < 60:
        split = (50, 50)
        reason = "Capacity or risk constraints require a balanced dual-source split."
    elif gap >= 15 and primary_risk >= 80 and primary_performance >= 90:
        split = (90, 10)
        reason = "The primary supplier has a strong, validated advantage while a continuity allocation is retained."
    elif gap >= 10:
        split = (80, 20)
        reason = "A meaningful score advantage supports concentration with a protected backup share."
    elif gap >= 5:
        split = (70, 30)
        reason = "Moderate differentiation supports a 70/30 risk-balanced split."
    else:
        split = (60, 40)
        reason = "Close supplier scores justify preserving competition and continuity."

    split = min(SUPPORTED_SPLITS, key=lambda item: abs(item[0] - min(split[0], primary_capacity_share)))
    rows = [
        {
            "Supplier": primary["Supplier"],
            "Recommended Allocation %": float(split[0]),
            "Role": "Primary Supplier",
            "Estimated Annual TCO USD": split[0] / 100 * annual_volume * float(primary["adjusted_tco_unit_usd"]),
        },
        {
            "Supplier": secondary["Supplier"],
            "Recommended Allocation %": float(split[1]),
            "Role": "Continuity Supplier",
            "Estimated Annual TCO USD": split[1] / 100 * annual_volume * float(secondary["adjusted_tco_unit_usd"]),
        },
    ]
    return {
        "allocation_df": pd.DataFrame(rows),
        "explanation": f"Recommend {split[0]}/{split[1]} between {primary['Supplier']} and {secondary['Supplier']}. {reason}",
    }
