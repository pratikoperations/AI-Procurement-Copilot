"""Extended supplier ESG maturity intelligence."""


def _clip(value):
    return round(max(0.0, min(100.0, float(value))), 1)


def evaluate_supplier_esg(row):
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
    maturity = _clip(environmental * 0.50 + social * 0.25 + governance_score * 0.25)
    level = "Leading" if maturity >= 85 else "Advanced" if maturity >= 75 else "Developing" if maturity >= 60 else "Basic" if maturity >= 45 else "High Risk"
    strengths = [name for name, value in {"Environmental": environmental, "Social": social, "Governance": governance_score}.items() if value >= 75]
    gaps = [name for name, value in {"Environmental": environmental, "Social": social, "Governance": governance_score}.items() if value < 60]
    documents = ["Environmental certifications", "Labor compliance declaration", "Human-rights policy", "Carbon data", "Sustainability roadmap"]
    actions = [f"Close {gap.lower()} evidence and corrective-action gaps." for gap in gaps] or ["Maintain annual ESG evidence refresh."]
    return {
        "environmental_score": environmental,
        "social_score": social,
        "governance_score": governance_score,
        "esg_maturity_score": maturity,
        "esg_maturity_level": level,
        "esg_strengths": strengths or ["No leading dimension confirmed"],
        "esg_gaps": gaps,
        "required_documentation": documents,
        "corrective_actions": actions,
    }
