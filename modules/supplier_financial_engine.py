"""Supplier financial health indicators based only on available data."""


def evaluate_supplier_financial_health(row):
    utilization = float(row.get("Capacity Utilization %", max(0, 100 - float(row.get("Capacity Buffer %", 10)))))
    buyer_dependency = float(row.get("Buyer Dependency %", 20))
    revenue_concentration = float(row.get("Revenue Concentration %", 35))
    payment = str(row.get("Payment Terms", "Net 30")).lower()
    advance_stress = 20 if "advance" in payment else 0
    completeness_fields = ["Capacity Utilization %", "Buyer Dependency %", "Revenue Concentration %"]
    completeness = sum(field in row for field in completeness_fields) / len(completeness_fields) * 100
    penalty = max(0, utilization - 80) * 0.7 + max(0, buyer_dependency - 30) * 0.5 + max(0, revenue_concentration - 50) * 0.4 + advance_stress
    score = round(max(0, min(100, 100 - penalty)), 1)
    category = "Low" if score >= 75 else "Medium" if score >= 55 else "High" if score >= 35 else "Critical"
    evidence = [f"Capacity utilization indicator: {utilization:.0f}%", f"Buyer dependency indicator: {buyer_dependency:.0f}%", f"Financial data completeness: {completeness:.0f}%"]
    actions = ["Complete credit and financial due diligence.", "Validate customer concentration and liquidity headroom."] if completeness < 100 or category in {"High", "Critical"} else ["Refresh financial review annually."]
    return {"financial_stability_score": score, "dependency_risk": "High" if buyer_dependency > 40 else "Medium" if buyer_dependency > 25 else "Low", "working_capital_risk": "High" if advance_stress else "Medium" if "net 30" in payment else "Low", "capacity_stress_indicator": "High" if utilization > 90 else "Medium" if utilization > 80 else "Low", "financial_risk_category": category, "evidence": evidence, "due_diligence_actions": actions, "data_completeness_score": round(completeness,1), "disclaimer": "Financial health indicator only; not audited financial analysis or bankruptcy probability."}
