"""Rule-guided procurement sourcing strategy engine."""


def recommend_strategy(scored_df, annual_volume):
    supplier_count = len(scored_df)
    top = scored_df.iloc[0]
    second = scored_df.iloc[1] if supplier_count > 1 else None
    score_gap = float(top["total_score"] - second["total_score"]) if second is not None else 100.0
    top_risk = float(top["risk_score"])
    top_performance = float(top["performance_score"])
    capacity = float(top.get("Supplier Capacity", annual_volume))

    if supplier_count == 1:
        strategy = "Single Source"
        reason = "Only one qualified supplier is available; formal continuity mitigation is required."
    elif top_risk < 60 or capacity < annual_volume:
        strategy = "Dual Source"
        reason = "Risk or capacity constraints justify a primary and continuity supplier."
    elif score_gap <= 5:
        strategy = "Competitive Tender"
        reason = "Supplier scores are close enough to preserve competition and commercial tension."
    elif top_performance >= 90 and top_risk >= 80 and score_gap >= 12:
        strategy = "Strategic Partnership"
        reason = "The leading supplier has a material performance and risk advantage suitable for deeper collaboration."
    elif annual_volume >= 250000 and top_risk >= 70:
        strategy = "Long-Term Agreement"
        reason = "Meaningful recurring demand and acceptable supplier risk support a longer-term commercial framework."
    else:
        strategy = "Dual Source"
        reason = "Balanced allocation protects continuity while retaining competitive leverage."

    return {
        "strategy": strategy,
        "reason": reason,
        "score_gap": round(score_gap, 1),
        "recommended_term": "12–24 months" if strategy in {"Long-Term Agreement", "Strategic Partnership"} else "Sourcing-event specific",
        "governance_note": "Revalidate market conditions, capacity, and supplier risk before contract signature.",
    }
