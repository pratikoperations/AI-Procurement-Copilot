"""Supplier innovation maturity intelligence with evidence governance."""


def _clip(value):
    return round(max(0.0, min(100.0, float(value))), 1)


def _present(row, field):
    return field in row and row.get(field) not in (None, "")


def evaluate_supplier_innovation(row, category="Packaging Procurement"):
    field_map = {
        "Design": "Design Capability Score",
        "Packaging": "Packaging Innovation Score",
        "Material": "Material Innovation Score",
        "Cost Reduction": "Cost Reduction Ideas Score",
        "Automation": "Automation Score",
        "Digital": "Digital Maturity Score",
        "Data Sharing": "Data Sharing Score",
        "AI Readiness": "AI Readiness Score",
        "Continuous Improvement": "Continuous Improvement Score",
        "Sustainability": "Sustainability Innovation Score",
        "Prototype Speed": "Prototype Speed Score",
    }
    defaults = {
        "Design": 60, "Packaging": 65 if category == "Packaging Procurement" else 50,
        "Material": 65, "Cost Reduction": 60, "Automation": 60,
        "Digital": 60, "Data Sharing": 55, "AI Readiness": 45,
        "Continuous Improvement": 65, "Sustainability": 60, "Prototype Speed": 60,
    }
    dimensions = {label: float(row.get(field, defaults[label])) for label, field in field_map.items()}
    completeness = sum(_present(row, field) for field in field_map.values()) / len(field_map) * 100
    raw_score = _clip(sum(dimensions.values()) / len(dimensions))

    if completeness < 40:
        assessment_status = "Insufficient Data"
        displayed_score = min(raw_score, 50.0)
        level = "Basic" if displayed_score >= 45 else "Low"
        evidence_quality = "Low"
        verification_required = True
    elif completeness < 70:
        assessment_status = "Limited Evidence"
        displayed_score = min(raw_score, 70.0)
        level = "Developing" if displayed_score >= 60 else "Basic" if displayed_score >= 45 else "Low"
        evidence_quality = "Limited"
        verification_required = True
    elif completeness < 85:
        assessment_status = "Sufficient With Review"
        displayed_score = raw_score
        level = "Leading" if displayed_score >= 85 else "Advanced" if displayed_score >= 75 else "Developing" if displayed_score >= 60 else "Basic" if displayed_score >= 45 else "Low"
        evidence_quality = "Moderate"
        verification_required = True
    else:
        assessment_status = "Sufficient Evidence"
        displayed_score = raw_score
        level = "Leading" if displayed_score >= 85 else "Advanced" if displayed_score >= 75 else "Developing" if displayed_score >= 60 else "Basic" if displayed_score >= 45 else "Low"
        evidence_quality = "Strong"
        verification_required = False

    strengths = [name for name, value in dimensions.items() if value >= 75 and completeness >= 70]
    gaps = [name for name, value in dimensions.items() if value < 55]
    if completeness < 70:
        gaps.append("Evidence completeness")
    opportunities = [
        "Joint value-engineering workshop",
        "Supplier-led cost-reduction pipeline",
        "Sustainability innovation roadmap",
        "Digital data-sharing pilot",
    ]
    return {
        "innovation_score": displayed_score,
        "displayed_innovation_score": displayed_score,
        "raw_innovation_score": raw_score,
        "innovation_maturity_level": level,
        "innovation_data_completeness": round(completeness, 1),
        "assessment_status": assessment_status,
        "evidence_quality": evidence_quality,
        "verification_required": verification_required,
        "innovation_dimensions": dimensions,
        "innovation_strengths": strengths or ["No verified leading capability confirmed"],
        "innovation_gaps": list(dict.fromkeys(gaps)),
        "collaboration_opportunities": opportunities,
        "recommended_innovation_agenda": "Prioritize two measurable initiatives with value, owner, timeline, and implementation gate.",
    }
