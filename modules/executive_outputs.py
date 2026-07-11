"""Executive memo, supplier email, explainability, and interview output generators."""

from modules.recommendation import award_status


def _eligibility_heading(status):
    return {
        "Blocked": "FINAL AWARD RECOMMENDATION WITHHELD",
        "Insufficient Data": "FINAL AWARD RECOMMENDATION WITHHELD",
        "Human Review Required": "PROVISIONAL RECOMMENDATION — HUMAN REVIEW REQUIRED",
        "Eligible With Conditions": "PROVISIONAL RECOMMENDATION — CONDITIONS APPLY",
        "Eligible": "EXECUTIVE SOURCING RECOMMENDATION",
    }.get(status, "PROVISIONAL SOURCING ASSESSMENT")


def generate_executive_memo(scored_df, allocation_df, value_metrics, confidence, eligibility=None, data_confidence=None):
    """Generate an eligibility-aware executive sourcing memo."""
    recommended = scored_df.iloc[0]
    lowest = scored_df.sort_values("Quoted Unit Price USD").iloc[0]
    eligibility = eligibility or {"status": "Eligible", "reason": "Eligibility checks passed.", "failed_checks": [], "required_remediation": []}
    status = eligibility.get("status", award_status(recommended, confidence))
    heading = _eligibility_heading(status)
    confidence_text = "Not available" if not data_confidence else f"{data_confidence.get('data_confidence_score', 0)}/100 — {data_confidence.get('confidence_category', 'Not assessed')}"

    if status in {"Blocked", "Insufficient Data"}:
        issues = "\n".join(f"- {item}" for item in eligibility.get("failed_checks", [])) or f"- {eligibility.get('reason', 'Validation failed.')}"
        remediation = "\n".join(f"- {item}" for item in eligibility.get("required_remediation", [])) or "- Resolve all blocking validation issues."
        return f"""{heading}

Status: {status}
Reason: {eligibility.get('reason', 'Critical validation issues prevent a defensible award recommendation.')}

Blocking or limiting issues:
{issues}

Required remediation:
{remediation}

Data confidence: {confidence_text}
Human approval requirement: Final supplier selection remains prohibited until all blocking issues are closed and documented approval is obtained.
""".strip()

    allocation_text = allocation_df[["Supplier", "Recommended Allocation %", "Role"]].to_string(index=False)
    return f"""{heading}

Recommended supplier: {recommended['Supplier']}
Decision status: {status}

Why selected:
{recommended['Supplier']} provides the strongest weighted procurement value after considering quoted price, risk-adjusted TCO, risk resilience, working capital, inventory exposure, ESG, and supplier performance.

Why the lowest quote may not win:
{lowest['Supplier']} has the lowest quoted price, but lowest quote is not automatically best value. The model also considers MOQ, freight, payment terms, lead time, quality, ESG readiness, and continuity exposure.

Financial impact:
- Annual TCO: ${recommended['annual_tco_usd']:,.0f}
- Market quote gap: ${value_metrics['market_quote_gap_usd']:,.0f}
- Negotiation headroom: ${value_metrics['negotiation_headroom_usd']:,.0f}
- Estimated EBITDA opportunity: ${value_metrics['estimated_ebitda_opportunity_usd']:,.0f}

Risk and governance:
- Risk resilience score: {recommended['risk_score']}/100
- Risk category: {recommended['risk_category']}
- Data confidence: {confidence_text}
- Human approval remains mandatory.

Recommended allocation:
{allocation_text}
""".strip()


def generate_supplier_email(recommended_supplier, should_cost_target, annual_volume, category="Packaging Procurement", commodity="Category", unit="piece", eligibility=None):
    """Generate category-aware and validation-aware supplier clarification email."""
    eligibility = eligibility or {"status": "Eligible", "reason": "Eligibility checks passed.", "failed_checks": []}
    status = eligibility.get("status", "Eligible")
    supplier = recommended_supplier["Supplier"]
    price = recommended_supplier["Quoted Unit Price USD"]

    if status == "Blocked":
        opening = "The current evaluation is paused because a blocking validation issue must be resolved before supplier comparison or award consideration can continue."
    elif status == "Insufficient Data":
        opening = "The current evaluation remains provisional because required commercial or operational information is incomplete."
    elif status == "Human Review Required":
        opening = "The current evaluation remains subject to internal procurement review and does not represent a final supplier selection."
    elif status == "Eligible With Conditions":
        opening = "The current evaluation may proceed only after the stated commercial and governance conditions are closed."
    else:
        opening = "Your proposal has progressed to commercial-alignment review; this does not constitute a final award."

    issue_text = "; ".join(eligibility.get("failed_checks", [])) or eligibility.get("reason", "No blocking issue recorded.")
    if category == "Raw Material Procurement":
        topics = [
            "Commodity index reference, publication source, and reset frequency",
            "Producer or conversion premium and supplier margin",
            "Grade, quality specification, and certificate of analysis",
            "Freight, duty, FX basis, and landed-cost assumptions",
            "Volume rebate and payment-term improvement",
            "Capacity allocation, supply assurance, and contingency supply",
            "Lead-time commitment and service-level protection",
            "Regulatory and compliance documentation",
        ]
        if commodity == "PET Resin":
            topics.insert(2, "PET resin grade, intrinsic viscosity specification, and approved application")
    else:
        topics = [
            "Material specification, conversion, printing, tooling or plate assumptions",
            "Scrap, freight, overhead, and margin assumptions",
            "Volume-linked price improvement and payment terms",
            "MOQ flexibility and lead-time commitments",
            "Recyclability, PCR content, EPR, certification, and quality documentation",
            "Service-level and continuity commitments",
        ]
    numbered = "\n".join(f"{i}. {text}" for i, text in enumerate(topics, 1))

    return f"""Subject: Clarification and Commercial Alignment — {commodity} RFQ

Dear {supplier} Team,

Thank you for submitting your proposal.

{opening}

Current validation status: {status}
Validation note: {issue_text}

Our current normalized comparison indicates a should-cost reference near ${should_cost_target:.4f} per {unit}, while your normalized quoted price is ${price:.4f} per {unit}. The annual requirement is {annual_volume:,.0f} {unit}.

Please clarify the following:
{numbered}

Please note that this request is for clarification and commercial alignment only. It does not imply supplier selection or award approval.

Best regards,
[Your Name]
Strategic Sourcing / Procurement Team
""".strip()


def generate_explainability_panel(recommended_supplier):
    """Generate explainable recommendation text."""
    return f"""Recommendation Logic Summary:

The engine ranks {recommended_supplier['Supplier']} highest after combining:
- TCO score: {recommended_supplier['tco_score']:.1f}/100
- Risk resilience score: {recommended_supplier['risk_score']:.1f}/100
- Lead-time score: {recommended_supplier['lead_time_score']:.1f}/100
- Payment score: {recommended_supplier['payment_score']:.1f}/100
- MOQ score: {recommended_supplier['moq_score']:.1f}/100
- Performance score: {recommended_supplier['performance_score']:.1f}/100
- ESG score: {recommended_supplier['esg_score']:.1f}/100
- Overall decision score: {recommended_supplier['total_score']:.1f}/100

The commercial scoring logic remains transparent, auditable, and subject to human procurement approval.
""".strip()


def generate_interview_talking_points():
    return """This AI Procurement Copilot converts RFQ data into category-aware, validation-gated sourcing decisions. It separates original quotation data from normalized comparison data, uses category-specific communication, distinguishes governed displayed scores from raw audit indicators, and withholds award language when validation fails. The system supports procurement judgment rather than replacing it."""
