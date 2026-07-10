"""Executive memo, supplier email, explainability, and interview output generators."""

from modules.recommendation import award_status


def generate_executive_memo(scored_df, allocation_df, value_metrics, confidence):
    """Generate executive sourcing memo."""
    recommended = scored_df.iloc[0]
    lowest = scored_df.sort_values("Quoted Unit Price USD").iloc[0]
    status = award_status(recommended, confidence)

    allocation_text = allocation_df[["Supplier", "Recommended Allocation %", "Role"]].to_string(index=False)

    return f"""
Executive Recommendation:
Award to {recommended['Supplier']}.

Decision Status:
{status}

Why:
{recommended['Supplier']} provides the strongest weighted procurement value after adjusting for quoted price, risk-adjusted TCO, supplier risk, working capital, inventory exposure, ESG, and supplier performance.

Why Not Lowest Price:
{lowest['Supplier']} has the lowest quoted price, but lowest quote is not automatically best value. The model adjusts for MOQ, freight exposure, payment terms, lead time, quality history, ESG readiness, and continuity exposure.

Financial Impact:
- Annual TCO: ${recommended['annual_tco_usd']:,.0f}
- Market quote gap: ${value_metrics['market_quote_gap_usd']:,.0f}
- Negotiation headroom: ${value_metrics['negotiation_headroom_usd']:,.0f}
- Estimated EBITDA opportunity: ${value_metrics['estimated_ebitda_opportunity_usd']:,.0f}

Key Risk Signals:
- Risk category: {recommended['risk_category']}
- Risk score: {recommended['risk_score']}/100
- Failure probability: {recommended['failure_probability']:.1%}
- EMV risk penalty: ${recommended['risk_penalty_usd']:.4f} per unit

Mitigation Actions:
1. Negotiate toward should-cost target.
2. Lock OTIF, quality PPM, documentation, and ESG commitments.
3. Use allocation split to maintain continuity and leverage.
4. Track supplier performance quarterly.
5. Review risk assumptions before final award.

Recommended Allocation:
{allocation_text}
""".strip()


def generate_supplier_email(recommended_supplier, should_cost_target, annual_volume):
    """Generate supplier clarification email."""
    return f"""
Subject: Commercial Alignment Discussion — RFQ Review

Dear {recommended_supplier['Supplier']} Team,

Thank you for submitting your proposal for the current sourcing requirement.

After reviewing your quotation against our should-cost baseline, supplier comparison, annual volume, risk-adjusted total cost of ownership model, risk scorecard, ESG expectations, and supplier performance benchmarks, your proposal appears operationally strong but still has scope for commercial alignment.

Our analysis indicates a should-cost target near ${should_cost_target:.4f}, while your current quoted price is ${recommended_supplier['Quoted Unit Price USD']:.4f}. Given the annual volume of {annual_volume:,.0f} units, we would like to discuss a revised offer that improves cost competitiveness while maintaining your current service, quality, ESG, and delivery commitments.

Specifically, we would like to review:
1. Raw material, conversion, printing, tooling, freight, overhead, and margin assumptions
2. Scope for volume-linked price improvement
3. Payment term improvement
4. MOQ flexibility
5. Freight, documentation, and service cost elements
6. Index-linked pricing formula
7. ESG, certification, EPR, and quality documentation support
8. Lead-time protection and service-level commitments
9. Risk-mitigation actions that can reduce the TCO risk premium

Please confirm your availability for a commercial alignment discussion this week.

Best regards,
[Your Name]
Strategic Sourcing / Procurement Team
""".strip()


def generate_explainability_panel(recommended_supplier):
    """Generate AI-style explainable recommendation text."""
    return f"""
Recommendation Logic Summary:

The engine recommends {recommended_supplier['Supplier']} because it ranks highest after combining:

- TCO score: {recommended_supplier['tco_score']:.1f}/100
- Risk score: {recommended_supplier['risk_score']:.1f}/100
- Lead-time score: {recommended_supplier['lead_time_score']:.1f}/100
- Payment score: {recommended_supplier['payment_score']:.1f}/100
- MOQ score: {recommended_supplier['moq_score']:.1f}/100
- Performance score: {recommended_supplier['performance_score']:.1f}/100
- ESG score: {recommended_supplier['esg_score']:.1f}/100
- Total weighted score: {recommended_supplier['total_score']:.1f}/100

This is a transparent rule-guided copilot. The AI-style layer explains the recommendation, but the commercial scoring logic remains auditable and controlled by procurement.
""".strip()


def generate_interview_talking_points():
    """Generate interview talking points for the project demo."""
    return """
How to explain this demo in an interview:

This is a working AI Procurement Copilot MVP designed to convert RFQ data into decision-ready sourcing output.

It supports synthetic demo data and uploaded RFQ files, normalizes supplier quotations, calculates packaging should-cost, evaluates risk-adjusted TCO, scores supplier risk, includes ESG and supplier performance, compares lowest price versus best value, recommends allocation under constraints, runs scenario stress tests, estimates negotiation headroom, and generates executive recommendations and supplier communication drafts.

The decision model is transparent and rule-guided because procurement decisions require explainability, auditability, and human control. AI can support document extraction, deviation detection, summarization, scenario explanation, negotiation drafting, and email generation, while the commercial scoring logic remains visible to procurement, finance, quality, supply chain, and business stakeholders.

The key point is that the tool does not simply select the lowest quote. It separates quoted price from true procurement value by adjusting for MOQ, inventory exposure, payment terms, freight responsibility, lead time, quality history, ESG readiness, working-capital impact, risk-adjusted continuity exposure, and macro supply shocks.
""".strip()
