"""Recommendation eligibility gate for procurement award outputs."""

from __future__ import annotations


def evaluate_recommendation_eligibility(
    rfq_validation: dict,
    business_rules: dict,
    data_confidence: dict,
    scored_df,
    annual_volume: float,
    min_risk_score: float = 0,
) -> dict:
    """Return the governed recommendation status and remediation requirements."""
    failed_checks = []
    remediation = []

    if not rfq_validation.get("is_valid", False):
        failed_checks.extend(rfq_validation.get("errors", []))
        remediation.append("Correct RFQ schema and required-field errors.")

    blocking = business_rules.get("blocking_issues", [])
    if blocking:
        failed_checks.extend(blocking)
        remediation.append("Resolve all blocking business-rule violations.")

    try:
        volume = float(annual_volume)
    except (TypeError, ValueError):
        volume = 0
    if volume <= 0:
        failed_checks.append("Annual volume is not valid.")
        remediation.append("Enter annual volume greater than zero.")

    if scored_df is None or getattr(scored_df, "empty", True):
        failed_checks.append("No scored suppliers are available.")
        remediation.append("Provide at least one valid supplier record.")
    else:
        if "risk_score" in scored_df.columns and not (scored_df["risk_score"] >= float(min_risk_score)).any():
            failed_checks.append("No supplier meets the minimum risk-score threshold.")
            remediation.append("Qualify another supplier, reduce exposure, or approve a documented exception.")

    confidence_score = float(data_confidence.get("data_confidence_score", 0))
    confidence_category = data_confidence.get("confidence_category", "Insufficient Data")

    if failed_checks:
        status = "Blocked"
        reason = "Critical validation or business-rule failures prevent a defensible award recommendation."
    elif confidence_score < 50:
        status = "Insufficient Data"
        reason = "Data completeness is too low for a final recommendation."
        remediation.append("Close critical data gaps and reduce reliance on defaults.")
    elif confidence_score < 70:
        status = "Human Review Required"
        reason = "The available data supports analysis only; the recommendation must remain provisional."
        remediation.append("Complete a documented human review before any sourcing decision.")
    elif business_rules.get("non_blocking_issues") or rfq_validation.get("warnings") or confidence_score < 85:
        status = "Eligible With Conditions"
        reason = "The recommendation is usable only with the listed conditions and human approval."
        remediation.append("Review warnings, validate assumptions, and document approval conditions.")
    else:
        status = "Eligible"
        reason = "Required checks passed with strong data completeness; human approval remains mandatory."
        remediation.append("Proceed to commercial, legal, quality, risk, and executive review.")

    return {
        "status": status,
        "reason": reason,
        "failed_checks": list(dict.fromkeys(failed_checks)),
        "required_remediation": list(dict.fromkeys(remediation)),
        "release_warning": "Do not treat this status as autonomous supplier approval.",
        "human_approval_requirement": "Mandatory for every award, allocation, classification, and contract decision.",
        "confidence_category": confidence_category,
        "recommendation_allowed": status in {"Eligible", "Eligible With Conditions", "Human Review Required"},
        "final_award_language_allowed": status in {"Eligible", "Eligible With Conditions"},
    }
