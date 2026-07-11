"""Supplier-level negotiation intelligence."""

import pandas as pd


def build_negotiation_intelligence(scored_df, annual_volume, should_cost_target=None):
    rows = []
    lowest_quote = float(scored_df["Quoted Unit Price USD"].min())
    target_reference = float(should_cost_target) if should_cost_target else lowest_quote

    for _, row in scored_df.iterrows():
        quote = float(row["Quoted Unit Price USD"])
        tco = float(row["adjusted_tco_unit_usd"])
        target_price = min(quote * 0.97, max(target_reference, quote * 0.90))
        walk_away = min(tco, quote * 1.02)
        saving = max((quote - target_price) * annual_volume, 0.0)
        leverage = []
        if quote > lowest_quote:
            leverage.append("price above market low")
        if float(row.get("MOQ", 0)) > float(scored_df["MOQ"].median()):
            leverage.append("high MOQ")
        if float(row.get("Lead Time Days", 0)) > float(scored_df["Lead Time Days"].median()):
            leverage.append("long lead time")
        if float(row.get("payment_score", 0)) < 50:
            leverage.append("weak payment terms")
        if float(row.get("risk_score", 0)) < 70:
            leverage.append("risk mitigation required")
        priority_score = (quote / max(lowest_quote, 0.0001) - 1) * 100 + max(0, 75 - float(row.get("risk_score", 75)))
        priority = "High" if priority_score >= 20 else "Medium" if priority_score >= 8 else "Low"
        rows.append(
            {
                "Supplier": row["Supplier"],
                "Negotiation Priority": priority,
                "Target Price USD": round(target_price, 4),
                "Walk-Away Price USD": round(walk_away, 4),
                "Expected Annual Savings USD": round(saving, 2),
                "Negotiation Leverage": ", ".join(leverage) or "maintain competitive tension",
                "Suggested Concessions": "Price reduction; improved payment terms; MOQ flexibility; lead-time commitment; service credits",
                "Commercial Opportunities": "Freight transparency; indexation formula; capacity reservation; rebate linked to volume",
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["Negotiation Priority", "Expected Annual Savings USD"],
        ascending=[True, False],
        key=lambda series: series.map({"High": 0, "Medium": 1, "Low": 2}) if series.name == "Negotiation Priority" else series,
    ).reset_index(drop=True)
