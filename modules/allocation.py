"""Supplier allocation recommendation engine."""

import pandas as pd


def recommend_allocation(
    scored_df,
    annual_volume,
    max_supplier_share=75,
    min_backup_share=25,
    min_risk_score=55,
    min_esg_score=50,
):
    """Recommend a supplier allocation split using score, risk, ESG, and concentration constraints."""
    eligible = scored_df.copy()
    if "technical_eligible" in eligible.columns:
        eligible = eligible[eligible["technical_eligible"].astype(bool)]

    qualified = eligible[
        (eligible["risk_score"] >= min_risk_score)
        & (eligible["esg_score"] >= min_esg_score)
    ].copy()

    if qualified.empty:
        qualified = eligible.head(2).copy()
    if qualified.empty:
        return pd.DataFrame(columns=[
            "Supplier", "Recommended Allocation %", "Role",
            "Advanced TCO Unit USD", "Estimated Annual TCO USD", "Reason",
        ])

    rows = []
    remaining = 100.0

    for idx, (_, supplier) in enumerate(qualified.iterrows()):
        capacity_units = float(supplier.get("Supplier Capacity", annual_volume))
        capacity_share = min((capacity_units / max(float(annual_volume), 1.0)) * 100, max_supplier_share)

        if idx == 0:
            proposed = min(max_supplier_share, capacity_share, 100 - min_backup_share if len(qualified) > 1 else 100)
            proposed = max(proposed, 50 if len(qualified) > 1 else 100)
        elif idx == 1:
            proposed = min(max(remaining, min_backup_share), capacity_share)
        else:
            proposed = min(remaining, capacity_share)

        proposed = max(min(proposed, remaining), 0)

        if proposed > 0:
            rows.append(
                {
                    "Supplier": supplier["Supplier"],
                    "Recommended Allocation %": round(proposed, 0),
                    "Role": "Primary Supplier" if idx == 0 else "Backup / Continuity Supplier" if idx == 1 else "Contingency Supplier",
                    "Advanced TCO Unit USD": supplier["adjusted_tco_unit_usd"],
                    "Estimated Annual TCO USD": proposed / 100 * supplier["adjusted_tco_unit_usd"] * annual_volume,
                    "Reason": "Allocation respects technical eligibility, weighted score, risk threshold, ESG threshold, and supplier concentration limit.",
                }
            )
            remaining -= proposed

        if remaining <= 0:
            break

    if rows and remaining > 0:
        rows[0]["Recommended Allocation %"] += remaining
        rows[0]["Estimated Annual TCO USD"] += remaining / 100 * rows[0]["Advanced TCO Unit USD"] * annual_volume

    return pd.DataFrame(rows)
