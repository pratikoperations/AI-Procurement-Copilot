"""Extended supplier performance intelligence."""


def _clip(value):
    return round(max(0.0, min(100.0, float(value))), 1)


def evaluate_supplier_performance(row):
    otif = float(row.get("OTIF %", 85))
    ppm = float(row.get("Quality PPM", 1500))
    audit = float(row.get("Audit Score", 70))
    complaints = float(row.get("Complaint Rate %", 3))
    responsiveness = float(row.get("Responsiveness Score", 70))
    service = float(row.get("Service Score", 70))
    cost = float(row.get("tco_score", 70))
    corrective = float(row.get("Corrective Action Closure %", 75))
    improvement = float(row.get("Continuous Improvement Score", 65))
    capacity = float(row.get("Capacity Buffer %", 10))
    lead = float(row.get("Lead Time Days", 30))
    innovation = float(row.get("Innovation Contribution Score", 60))

    quality_score = _clip((100 - min(ppm / 25, 60)) * 0.55 + audit * 0.30 + (100 - complaints * 10) * 0.15)
    delivery_score = _clip(otif * 0.75 + max(0, 100 - lead * 1.5) * 0.25)
    service_score = _clip(responsiveness * 0.5 + service * 0.5)
    commercial_score = _clip(cost * 0.7 + min(capacity * 4, 100) * 0.3)
    improvement_score = _clip(corrective * 0.45 + improvement * 0.35 + innovation * 0.20)
    overall = _clip(quality_score * 0.25 + delivery_score * 0.20 + service_score * 0.15 + commercial_score * 0.20 + improvement_score * 0.20)
    category = "Excellent" if overall >= 85 else "Strong" if overall >= 75 else "Acceptable" if overall >= 60 else "Weak" if overall >= 45 else "Critical"
    strengths = [name for name, score in {"Quality": quality_score, "Delivery": delivery_score, "Service": service_score, "Commercial": commercial_score, "Improvement": improvement_score}.items() if score >= 75]
    weaknesses = [name for name, score in {"Quality": quality_score, "Delivery": delivery_score, "Service": service_score, "Commercial": commercial_score, "Improvement": improvement_score}.items() if score < 60]
    actions = [f"Create improvement plan for {item.lower()} performance." for item in weaknesses] or ["Maintain quarterly continuous-improvement review."]
    return {
        "quality_score": quality_score,
        "delivery_score": delivery_score,
        "service_score": service_score,
        "commercial_score": commercial_score,
        "improvement_score": improvement_score,
        "overall_supplier_performance_score": overall,
        "performance_category": category,
        "key_strengths": strengths or ["Balanced performance"],
        "key_weaknesses": weaknesses,
        "supplier_development_actions": actions,
    }
