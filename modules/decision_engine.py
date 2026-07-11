"""Deterministic executive procurement decision engine."""


def _confidence(scored_df):
    if len(scored_df) < 2:
        return 60.0
    gap = float(scored_df.iloc[0]["total_score"] - scored_df.iloc[1]["total_score"])
    return round(min(95.0, max(55.0, 65.0 + gap * 2.5)), 1)


def build_explainability(scored_df):
    winner = scored_df.iloc[0]
    competitors = []
    for _, row in scored_df.iloc[1:].iterrows():
        reasons = []
        if row["adjusted_tco_unit_usd"] > winner["adjusted_tco_unit_usd"]:
            reasons.append("higher risk-adjusted TCO")
        if row["risk_score"] < winner["risk_score"]:
            reasons.append("weaker risk profile")
        if row["performance_score"] < winner["performance_score"]:
            reasons.append("weaker performance")
        competitors.append({"supplier": row["Supplier"], "reason": ", ".join(reasons) or "lower total weighted score"})
    factors = sorted(
        [
            ("TCO", float(winner.get("tco_score", 0))),
            ("Risk", float(winner.get("risk_score", 0))),
            ("Performance", float(winner.get("performance_score", 0))),
            ("ESG", float(winner.get("esg_score", 0))),
            ("Lead Time", float(winner.get("lead_time_score", 0))),
            ("Payment", float(winner.get("payment_score", 0))),
        ],
        key=lambda item: item[1],
        reverse=True,
    )
    return {
        "selected_supplier": winner["Supplier"],
        "why_selected": (
            f"{winner['Supplier']} leads the governed decision model with a total score of "
            f"{winner['total_score']}/100 and risk-adjusted TCO of ${winner['adjusted_tco_unit_usd']:.4f} per unit."
        ),
        "rejected_suppliers": competitors,
        "most_influential_factors": [name for name, _ in factors[:3]],
        "trade_offs": "The recommendation balances cost, continuity, risk, service, ESG, MOQ, lead time, and payment terms.",
        "assumptions": "Input data, scoring weights, scenario assumptions, and allocation constraints remain visible and user-controlled.",
        "governance": "Transparent, rule-guided, auditable, and not black-box AI.",
    }


def generate_decision(scored_df, allocation_df=None, risk_summary=None):
    winner = scored_df.iloc[0]
    lowest = scored_df.sort_values("Quoted Unit Price USD").iloc[0]
    confidence = _confidence(scored_df)
    allocation_text = "Primary award recommendation"
    if allocation_df is not None and not allocation_df.empty:
        allocation_text = "; ".join(
            f"{row['Supplier']} {row['Recommended Allocation %']:.0f}%" for _, row in allocation_df.iterrows()
        )
    risk_text = risk_summary.get("highest_severity", "Medium") if risk_summary else "Medium"
    lowest_note = (
        "The recommended supplier is also the lowest quoted supplier."
        if winner["Supplier"] == lowest["Supplier"]
        else f"{lowest['Supplier']} quoted lowest, but did not win after TCO, risk, service, ESG, and commercial adjustment."
    )
    explainability = build_explainability(scored_df)
    return {
        "recommended_supplier": winner["Supplier"],
        "award_confidence": confidence,
        "business_justification": lowest_note,
        "procurement_rationale": explainability["why_selected"],
        "risk_adjusted_recommendation": f"Proceed with {allocation_text}; overall risk severity is {risk_text}.",
        "executive_recommendation": (
            f"Recommend awarding business to {winner['Supplier']} under the proposed allocation. "
            f"Confidence is {confidence}/100. Validate final capacity, commercial terms, and continuity mitigations before award."
        ),
        "explainability": explainability,
    }


def generate_executive_narrative(decision, strategy, allocation, risks, financial_impact):
    mitigation = risks.get("top_mitigation", "Maintain qualified backup supply and contractual service protections.")
    return (
        f"SITUATION\nSupplier bids were evaluated beyond quoted price using TCO, risk, performance, ESG, MOQ, lead time, and payment terms.\n\n"
        f"ANALYSIS\n{decision['procurement_rationale']} {decision['business_justification']}\n\n"
        f"RECOMMENDATION\n{decision['executive_recommendation']} Strategy: {strategy['strategy']}. Allocation: {allocation['explanation']}\n\n"
        f"BUSINESS IMPACT\nImproves decision transparency, continuity protection, and negotiation readiness.\n\n"
        f"FINANCIAL IMPACT\nEstimated annual opportunity: ${financial_impact:,.0f}.\n\n"
        f"RISK\nHighest identified severity: {risks.get('highest_severity', 'Medium')}.\n\n"
        f"MITIGATION\n{mitigation}\n\n"
        f"NEXT STEPS\nValidate supplier capacity, close commercial clarifications, confirm allocation, and document award governance."
    )
