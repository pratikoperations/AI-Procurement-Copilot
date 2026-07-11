"""Build 0.9.6 orchestration for data confidence, rules, and eligibility."""

from __future__ import annotations
from modules.business_rule_validator import validate_business_rules
from modules.data_confidence import calculate_data_confidence
from modules.recommendation_eligibility import evaluate_recommendation_eligibility


def run_validation_assurance(suppliers_df, scored_df, allocation_df, supplier_profiles, assumptions, rfq_validation) -> dict:
    defaulted_fields = set()
    for profile in supplier_profiles or []:
        defaulted_fields.update(profile.get("defaults_used", []))
    source_label = "Synthetic demonstration data" if assumptions.get("data_source") == "Synthetic Demo" else "Uploaded supplier data — not independently verified"
    confidence = calculate_data_confidence(
        suppliers_df,
        defaulted_fields=defaulted_fields,
        inferred_fields=["risk_score", "total_score", "supplier360_score"],
        source_label=source_label,
    )
    rules = validate_business_rules(
        suppliers_df,
        annual_volume=assumptions.get("annual_volume", 0),
        allocation_df=allocation_df,
        supplier_profiles=supplier_profiles,
    )
    eligibility = evaluate_recommendation_eligibility(
        rfq_validation,
        rules,
        confidence,
        scored_df,
        annual_volume=assumptions.get("annual_volume", 0),
        min_risk_score=assumptions.get("min_risk_score", 0),
    )
    return {"data_confidence": confidence, "business_rules": rules, "eligibility": eligibility}


def safe_executive_text(eligibility: dict, approved_text: str, provisional_text: str | None = None) -> str:
    """Prevent final-award language while preserving already governed withheld reports."""
    status = eligibility.get("status")
    normalized = str(approved_text or "").lstrip()
    if status in {"Blocked", "Insufficient Data"} and normalized.startswith("FINAL AWARD RECOMMENDATION WITHHELD"):
        return approved_text
    if eligibility.get("final_award_language_allowed"):
        return approved_text
    if status == "Human Review Required" and provisional_text:
        if str(provisional_text).lstrip().startswith("PROVISIONAL RECOMMENDATION"):
            return provisional_text
        return "PROVISIONAL — HUMAN REVIEW REQUIRED\n\n" + provisional_text
    issues = eligibility.get("failed_checks", [])
    remediation = eligibility.get("required_remediation", [])
    return (
        f"FINAL AWARD RECOMMENDATION WITHHELD\n\nStatus: {status}\n"
        f"Reason: {eligibility.get('reason', 'Validation did not pass.')}\n\n"
        f"Blocking or limiting issues:\n- " + ("\n- ".join(issues) if issues else "Data confidence below release threshold")
        + "\n\nRequired remediation:\n- " + ("\n- ".join(remediation) if remediation else "Complete human review")
    )
