"""Supplier financial health indicators based only on available data."""


def _present(row, field):
    return field in row and row.get(field) not in (None, "")


def evaluate_supplier_financial_health(row):
    utilization = float(row.get("Capacity Utilization %", max(0, 100 - float(row.get("Capacity Buffer %", 10)))))
    buyer_dependency = float(row.get("Buyer Dependency %", 20))
    revenue_concentration = float(row.get("Revenue Concentration %", 35))
    payment = str(row.get("Payment Terms", "Net 30")).lower()
    advance_stress = 20 if "advance" in payment else 0

    completeness_fields = ["Capacity Utilization %", "Buyer Dependency %", "Revenue Concentration %"]
    completeness = sum(_present(row, field) for field in completeness_fields) / len(completeness_fields) * 100

    penalty = (
        max(0, utilization - 80) * 0.7
        + max(0, buyer_dependency - 30) * 0.5
        + max(0, revenue_concentration - 50) * 0.4
        + advance_stress
    )
    raw_score = round(max(0, min(100, 100 - penalty)), 1)

    if completeness < 40:
        assessment_status = "Insufficient Data"
        displayed_score = min(raw_score, 50.0)
        evidence_quality = "Low"
        due_diligence_required = True
        category = "Due Diligence Required"
        warning = "Financial evidence is insufficient. The displayed score is provisional and capped at 50."
    elif completeness < 70:
        assessment_status = "Limited Evidence"
        displayed_score = min(raw_score, 70.0)
        evidence_quality = "Limited"
        due_diligence_required = True
        category = "Provisional"
        warning = "Financial evidence is limited. Treat the assessment as provisional."
    elif completeness < 85:
        assessment_status = "Sufficient With Review"
        displayed_score = raw_score
        evidence_quality = "Moderate"
        due_diligence_required = True
        category = "Low" if raw_score >= 75 else "Medium" if raw_score >= 55 else "High" if raw_score >= 35 else "Critical"
        warning = "Evidence is usable with documented human review."
    else:
        assessment_status = "Sufficient Evidence"
        displayed_score = raw_score
        evidence_quality = "Strong"
        due_diligence_required = False
        category = "Low" if raw_score >= 75 else "Medium" if raw_score >= 55 else "High" if raw_score >= 35 else "Critical"
        warning = "Evidence completeness is strong; normal financial due diligence still applies."

    evidence = [
        f"Capacity utilization indicator: {utilization:.0f}%",
        f"Buyer dependency indicator: {buyer_dependency:.0f}%",
        f"Revenue concentration indicator: {revenue_concentration:.0f}%",
        f"Financial data completeness: {completeness:.0f}%",
    ]
    actions = [
        "Complete credit and financial due diligence.",
        "Validate customer concentration and liquidity headroom.",
        "Confirm working-capital resilience and payment-term exposure.",
    ] if due_diligence_required or category in {"High", "Critical"} else ["Refresh financial review annually."]

    return {
        "financial_stability_score": displayed_score,
        "displayed_financial_score": displayed_score,
        "raw_indicator_score": raw_score,
        "dependency_risk": "High" if buyer_dependency > 40 else "Medium" if buyer_dependency > 25 else "Low",
        "working_capital_risk": "High" if advance_stress else "Medium" if "net 30" in payment else "Low",
        "capacity_stress_indicator": "High" if utilization > 90 else "Medium" if utilization > 80 else "Low",
        "financial_risk_category": category,
        "assessment_status": assessment_status,
        "evidence_quality": evidence_quality,
        "evidence": evidence,
        "due_diligence_actions": actions,
        "due_diligence_required": due_diligence_required,
        "data_completeness_score": round(completeness, 1),
        "confidence_warning": warning,
        "disclaimer": "Financial health outputs are indicators only and are not audited financial analysis, credit ratings, insolvency forecasts, or bankruptcy probabilities.",
    }
