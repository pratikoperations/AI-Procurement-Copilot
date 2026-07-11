"""Extended supplier ESG maturity intelligence with evidence governance."""


def _clip(value):
    return round(max(0.0, min(100.0, float(value))), 1)


def _present(row, field):
    return field in row and row.get(field) not in (None, "")


def evaluate_supplier_esg(row):
    fields = [
        "Recyclability", "PCR Content %", "Carbon Score", "Certification",
        "EPR Readiness", "Renewable Energy %", "Labor Compliance Score",
        "Human Rights Score", "Governance Score", "Sustainability Roadmap Score",
    ]
    completeness = sum(_present(row, field) for field in fields) / len(fields) * 100

    recyclability = float(row.get("Recyclability", 60))
    pcr = float(row.get("PCR Content %", 5))
    carbon = float(row.get("Carbon Score", 60))
    certification = float(row.get("Certification", 60))
    epr = float(row.get("EPR Readiness", 60))
    renewable = float(row.get("Renewable Energy %", 20))
    labor = float(row.get("Labor Compliance Score", 70))
    human_rights = float(row.get("Human Rights Score", 70))
    governance = float(row.get("Governance Score", 70))
    roadmap = float(row.get("Sustainability Roadmap Score", 60))

    environmental = _clip(recyclability * 0.22 + min(pcr * 3, 100) * 0.13 + carbon * 0.20 + certification * 0.15 + epr * 0.15 + renewable * 0.15)
    social = _clip(labor * 0.55 + human_rights * 0.45)
    governance_score = _clip(governance * 0.65 + roadmap * 0.35)
    raw_score = _clip(environmental * 0.50 + social * 0.25 + governance_score * 0.25)

    if completeness < 40:
        assessment_status = "Insufficient Data"
        displayed_score = min(raw_score, 50.0)
        evidence_quality = "Low"
        level = "Basic" if displayed_score >= 45 else "High Risk"
        verification_required = True
    elif completeness < 70:
        assessment_status = "Limited Evidence"
        displayed_score = min(raw_score, 70.0)
        evidence_quality = "Limited"
        level = "Developing" if displayed_score >= 60 else "Basic" if displayed_score >= 45 else "High Risk"
        verification_required = True
    elif completeness < 85:
        assessment_status = "Sufficient With Review"
        displayed_score = raw_score
        evidence_quality = "Moderate"
        level = "Leading" if displayed_score >= 85 else "Advanced" if displayed_score >= 75 else "Developing" if displayed_score >= 60 else "Basic" if displayed_score >= 45 else "High Risk"
        verification_required = True
    else:
        assessment_status = "Sufficient Evidence"
        displayed_score = raw_score
        evidence_quality = "Strong"
        level = "Leading" if displayed_score >= 85 else "Advanced" if displayed_score >= 75 else "Developing" if displayed_score >= 60 else "Basic" if displayed_score >= 45 else "High Risk"
        verification_required = False

    strengths = [name for name, value in {"Environmental": environmental, "Social": social, "Governance": governance_score}.items() if value >= 75 and completeness >= 70]
    gaps = [name for name, value in {"Environmental": environmental, "Social": social, "Governance": governance_score}.items() if value < 60]
    if completeness < 70:
        gaps.append("Evidence completeness")
    documents = ["Environmental certifications", "Labor compliance declaration", "Human-rights policy", "Carbon data", "Sustainability roadmap"]
    actions = [f"Close {gap.lower()} evidence and corrective-action gaps." for gap in dict.fromkeys(gaps)] or ["Maintain annual ESG evidence refresh."]

    return {
        "environmental_score": environmental,
        "social_score": social,
        "governance_score": governance_score,
        "esg_maturity_score": displayed_score,
        "displayed_esg_score": displayed_score,
        "raw_esg_score": raw_score,
        "esg_maturity_level": level,
        "esg_data_completeness": round(completeness, 1),
        "assessment_status": assessment_status,
        "evidence_quality": evidence_quality,
        "verification_required": verification_required,
        "esg_strengths": strengths or ["No verified leading dimension confirmed"],
        "esg_gaps": list(dict.fromkeys(gaps)),
        "required_documentation": documents,
        "corrective_actions": actions,
    }
