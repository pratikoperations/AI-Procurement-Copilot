"""Supplier relationship management classification engine."""


def classify_supplier_relationship(row, performance, financial, esg, innovation):
    spend = str(row.get("Spend Classification", "Medium")).title()
    criticality = float(row.get("Business Criticality Score", 60))
    switching = float(row.get("Switching Difficulty Score", 55))
    concentration = float(row.get("Supplier Concentration %", 40))
    risk = float(row.get("risk_score", 60))
    perf = float(performance["overall_supplier_performance_score"])
    innov = float(innovation["innovation_score"])
    esg_score = float(esg["esg_maturity_score"])
    financial_score = float(financial["financial_stability_score"])

    strategic_index = perf * 0.25 + risk * 0.20 + innov * 0.15 + esg_score * 0.10 + financial_score * 0.10 + criticality * 0.10 + switching * 0.05 + min(concentration,100) * 0.05
    if perf < 45 or risk < 40 or financial_score < 35:
        classification = "Exit Candidate"
    elif perf < 60 or risk < 55:
        classification = "Development"
    elif strategic_index >= 80 and criticality >= 70:
        classification = "Strategic"
    elif strategic_index >= 70:
        classification = "Preferred"
    elif strategic_index >= 58:
        classification = "Approved"
    else:
        classification = "Transactional"

    settings = {
        "Strategic": ("High", "Monthly operational + quarterly executive", True, "Quarterly", "Co-create value, innovation, resilience, and long-term roadmap."),
        "Preferred": ("Medium-High", "Monthly operational review", False, "Quarterly", "Grow share selectively against performance commitments."),
        "Approved": ("Medium", "Quarterly scorecard", False, "Semi-annual", "Maintain qualification and competitive tension."),
        "Transactional": ("Low", "Exception-based", False, "Annual", "Use competitive sourcing and simplified governance."),
        "Development": ("High corrective", "Monthly corrective-action review", False, "Monthly", "Execute time-bound supplier-development plan."),
        "Exit Candidate": ("Controlled exit", "Monthly transition review", True, "Monthly", "Reduce exposure and qualify replacement supply."),
    }
    intensity, cadence, sponsor, review, strategy = settings[classification]
    return {
        "srm_classification": classification,
        "relationship_intensity": intensity,
        "governance_cadence": cadence,
        "executive_sponsor_required": sponsor,
        "review_frequency": review,
        "relationship_strategy": strategy,
        "classification_rationale": f"Classification reflects performance {perf:.1f}, risk {risk:.1f}, innovation {innov:.1f}, ESG {esg_score:.1f}, financial health {financial_score:.1f}, and business criticality {criticality:.1f}.",
        "strategic_index": round(max(0,min(100,strategic_index)),1),
        "spend_classification": spend,
    }
