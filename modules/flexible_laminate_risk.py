"""Deterministic risk and technical-eligibility controls for Flexible Laminates.

All capability and continuity inputs are synthetic demonstration assumptions.
They are not audited supplier evidence, laboratory results, or technical approvals.
"""

from __future__ import annotations

import math


ELIGIBILITY_THRESHOLDS = {
    "Substrate Availability %": (50.0, None),
    "Press Capacity Utilisation %": (None, 95.0),
    "Lamination Capacity Utilisation %": (None, 95.0),
    "Printing Capability Score": (70.0, None),
    "Lamination Capability Score": (70.0, None),
    "Bond Strength Continuity Score": (65.0, None),
    "Seal Integrity Continuity Score": (65.0, None),
    "Solvent Retention Control Score": (65.0, None),
}

RISK_FIELDS = tuple(ELIGIBILITY_THRESHOLDS)
TOOLING_AVAILABILITY_VALUES = {"Yes", "No", "Not assessed", "Not applicable"}
APPROVAL_VALUES = {"Approved", "Conditional", "Not approved"}


def _finite_number(record: dict, field: str) -> float:
    try:
        value = float(record[field])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"'{field}' must contain a finite numeric value for Flexible Laminates.") from exc
    if not math.isfinite(value):
        raise ValueError(f"'{field}' must contain a finite numeric value for Flexible Laminates.")
    if not 0 <= value <= 100:
        raise ValueError(f"'{field}' must be between 0 and 100 for Flexible Laminates.")
    return value


def effective_process_loss_pct(record: dict) -> float:
    """Return compounded printing, lamination, and slitting loss exposure."""
    printing = _finite_number(record, "Printing Loss %")
    lamination = _finite_number(record, "Lamination Loss %")
    slitting = _finite_number(record, "Slitting Loss %")
    if printing > 8:
        raise ValueError("'Printing Loss %' must be between 0 and 8 for Flexible Laminates.")
    if lamination > 6:
        raise ValueError("'Lamination Loss %' must be between 0 and 6 for Flexible Laminates.")
    if slitting > 5:
        raise ValueError("'Slitting Loss %' must be between 0 and 5 for Flexible Laminates.")
    effective = (1 - (1 - printing / 100) * (1 - lamination / 100) * (1 - slitting / 100)) * 100
    if effective >= 15:
        raise ValueError("Combined effective process loss must remain below 15%.")
    return effective


def assess_flexible_laminate_supplier(record: dict) -> dict:
    """Return deterministic C2 risk, failure probability, and eligibility."""
    values = {field: _finite_number(record, field) for field in RISK_FIELDS}
    approval = str(record.get("Application Approval Status", "")).strip()
    tooling = str(record.get("Tooling Availability", "")).strip()
    if approval not in APPROVAL_VALUES:
        raise ValueError("Application Approval Status must be Approved, Conditional, or Not approved.")
    if tooling not in TOOLING_AVAILABILITY_VALUES:
        raise ValueError("Tooling Availability must be Yes, No, Not assessed, or Not applicable.")

    loss = effective_process_loss_pct(record)
    reasons: list[str] = []
    for field, (minimum, maximum) in ELIGIBILITY_THRESHOLDS.items():
        value = values[field]
        if minimum is not None and value < minimum:
            reasons.append(f"{field} is below {minimum:.0f}.")
        if maximum is not None and value > maximum:
            reasons.append(f"{field} exceeds {maximum:.0f}.")
    if approval != "Approved":
        reasons.append("Application Approval Status is not Approved.")
    if str(record.get("Tooling Status", "")).strip() == "Existing" and tooling != "Yes":
        reasons.append("Existing tooling is not explicitly available.")

    # Higher score means stronger resilience, consistent with the shared engine.
    positive_resilience = (
        values["Substrate Availability %"] * 0.16
        + (100 - values["Press Capacity Utilisation %"]) * 0.10
        + (100 - values["Lamination Capacity Utilisation %"]) * 0.10
        + values["Printing Capability Score"] * 0.12
        + values["Lamination Capability Score"] * 0.12
        + values["Bond Strength Continuity Score"] * 0.12
        + values["Seal Integrity Continuity Score"] * 0.12
        + values["Solvent Retention Control Score"] * 0.10
        + max(0.0, 100 - loss * 6) * 0.06
    )
    approval_penalty = {"Approved": 0.0, "Conditional": 18.0, "Not approved": 40.0}[approval]
    tooling_penalty = 0.0 if tooling in {"Yes", "Not applicable"} else 8.0
    risk_score = max(0.0, min(100.0, positive_resilience - approval_penalty - tooling_penalty))
    failure_probability = max(0.01, min(0.75, (100 - risk_score) / 125 + loss / 250))
    risk_category = "Low" if risk_score >= 80 else "Medium" if risk_score >= 65 else "High" if risk_score >= 45 else "Critical"

    return {
        "technical_eligible": not reasons,
        "technical_ineligibility_reasons": reasons,
        "risk_score": round(risk_score, 1),
        "risk_category": risk_category,
        "failure_probability": round(failure_probability, 4),
        "effective_process_loss_pct": round(loss, 3),
        "risk_assumption_basis": "Synthetic C2 capability and continuity assumptions; human technical approval remains mandatory.",
    }


def apply_flexible_laminate_risk_to_tco(record: dict, annual_volume: float) -> dict:
    """Apply C2 risk premium to existing packaging TCO fields."""
    assessment = assess_flexible_laminate_supplier(record)
    base_tco = float(record["adjusted_tco_unit_usd"])
    premium = assessment["failure_probability"] * 0.12 + assessment["effective_process_loss_pct"] / 1000
    adjusted = base_tco * (1 + premium)
    assessment.update({
        "laminate_risk_premium_pct": round(premium * 100, 3),
        "adjusted_tco_unit_usd": adjusted,
        "annual_tco_usd": adjusted * float(annual_volume),
    })
    return assessment
