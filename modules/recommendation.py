"""Decision intelligence and executive recommendation engine."""

from modules.utils import normalize_score


def recommendation_confidence(scored_df):
    """Calculate recommendation confidence based on score gap, TCO gap, risk, performance, and ESG."""
    top = scored_df.iloc[0]
    second = scored_df.iloc[1] if len(scored_df) > 1 else top

    score_gap = max(float(top["total_score"]) - float(second["total_score"]), 0)
    tco_gap = max(float(second["adjusted_tco_unit_usd"]) - float(top["adjusted_tco_unit_usd"]), 0) / max(float(top["adjusted_tco_unit_usd"]), 0.0001) * 100

    confidence = (
        min(score_gap * 2.0, 25)
        + min(tco_gap * 1.5, 20)
        + float(top["risk_score"]) * 0.30
        + float(top["performance_score"]) * 0.20
        + float(top["esg_score"]) * 0.10
    )
    return round(normalize_score(confidence), 1)


def best_value_decision(scored_df):
    """Compare lowest quote against best-value supplier."""
    recommended = scored_df.iloc[0]
    lowest = scored_df.sort_values("Quoted Unit Price USD").iloc[0]

    if recommended["Supplier"] == lowest["Supplier"]:
        message = f"{recommended['Supplier']} is both the lowest quoted supplier and the best-value supplier."
    else:
        message = (
            f"{lowest['Supplier']} has the lowest quoted price, but {recommended['Supplier']} ranks higher after TCO, "
            "risk, ESG, payment terms, lead time, MOQ, and performance adjustment."
        )

    return {
        "recommended_supplier": recommended["Supplier"],
        "lowest_quote_supplier": lowest["Supplier"],
        "lowest_quote_price": float(lowest["Quoted Unit Price USD"]),
        "message": message,
    }


def executive_value_breakdown(scored_df, annual_volume, should_cost_target):
    """Calculate value metrics for executive sourcing discussion."""
    recommended = scored_df.iloc[0]
    lowest = scored_df.sort_values("Quoted Unit Price USD").iloc[0]
    highest = scored_df.sort_values("Quoted Unit Price USD").iloc[-1]

    market_quote_gap = (float(highest["Quoted Unit Price USD"]) - float(lowest["Quoted Unit Price USD"])) * annual_volume
    tco_vs_lowest = (float(lowest["adjusted_tco_unit_usd"]) - float(recommended["adjusted_tco_unit_usd"])) * annual_volume
    negotiation_headroom = max((float(recommended["Quoted Unit Price USD"]) - float(should_cost_target)) * annual_volume, 0)
    risk_score_advantage = float(recommended["risk_score"]) - float(lowest["risk_score"])

    return {
        "market_quote_gap_usd": round(market_quote_gap, 2),
        "tco_savings_or_premium_vs_lowest_usd": round(tco_vs_lowest, 2),
        "negotiation_headroom_usd": round(negotiation_headroom, 2),
        "risk_score_advantage": round(risk_score_advantage, 1),
        "estimated_ebitda_opportunity_usd": round(max(negotiation_headroom + max(tco_vs_lowest, 0), 0), 2),
    }


def award_status(recommended, confidence):
    """Return award status based on score, risk, and confidence."""
    if recommended["total_score"] >= 80 and recommended["risk_score"] >= 75 and confidence >= 75:
        return "Award Recommended"
    if recommended["total_score"] >= 70 and recommended["risk_score"] >= 60:
        return "Conditional Award Recommended"
    return "Do Not Award Without Mitigation"
