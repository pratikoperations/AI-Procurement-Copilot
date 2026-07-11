"""Explainable supplier recommendation rankings governed by evidence quality."""

GOVERNANCE_TEXT = "Transparent, rule-guided, auditable, and not black-box AI."

RECOMMENDATION_EXPLANATIONS = {
    "Best Value Supplier": "Highest overall value after balancing cost, performance, governance, and business risk.",
    "Lowest Cost Supplier": "Lowest normalized commercial price before risk and total-cost adjustments.",
    "Lowest Risk Supplier": "Strongest available operational, financial, and governance profile.",
    "Best Performer": "Highest operational performance across quality, delivery, service, and commercial execution.",
    "Most Innovative Supplier": "Highest demonstrated innovation capability among suppliers with sufficient evidence.",
    "Most Sustainable Supplier": "Strongest ESG maturity among suppliers with sufficient verified evidence.",
    "Best Strategic Partner": "Strongest qualified strategic fit for structured relationship governance and long-term collaboration.",
    "Best Long-Term Supplier": "Best qualified combined profile for continuity, performance, financial resilience, ESG, innovation, and strategic fit.",
    "Development Candidate": "Suitable for targeted capability improvement rather than immediate strategic award.",
    "Exit Candidate": "Requires corrective action and governance review before future sourcing consideration.",
}


def _flat(profile):
    financial = profile["financial"]
    esg = profile["esg"]
    innovation = profile["innovation"]
    return {
        "supplier_name": profile["supplier_name"],
        "supplier360": profile["overall_supplier360_score"],
        "performance": profile["performance"]["overall_supplier_performance_score"],
        "financial": financial.get("displayed_financial_score", financial.get("financial_stability_score", 0)),
        "financial_status": financial.get("assessment_status", "Insufficient Data"),
        "esg": esg.get("displayed_esg_score", esg.get("esg_maturity_score", 0)),
        "esg_status": esg.get("assessment_status", "Insufficient Data"),
        "esg_completeness": esg.get("esg_data_completeness", 0),
        "innovation": innovation.get("displayed_innovation_score", innovation.get("innovation_score", 0)),
        "innovation_status": innovation.get("assessment_status", "Insufficient Data"),
        "innovation_completeness": innovation.get("innovation_data_completeness", 0),
        "strategic": profile["srm"]["strategic_index"],
        "risk": float(profile.get("risk_score", 60)),
        "price": float(profile.get("quoted_price", 0)),
        "tco": float(profile.get("adjusted_tco", 0)),
        "classification": profile["srm"]["srm_classification"],
    }


def _result(role, winner=None, evidence_status="Sufficient", confidence="Medium", condition="Human approval required"):
    if winner is None:
        return {
            "Recommendation": role,
            "Supplier": "No Qualified Supplier",
            "Explanation": f"No supplier currently qualifies for {role} due to insufficient verified evidence or governance restrictions.",
            "Evidence Status": evidence_status,
            "Confidence": "Low",
            "Human Review Status": "Required",
            "Trade-Off": "The role remains unassigned until evidence and governance conditions are met.",
            "Qualification Condition": condition,
            "Governance": GOVERNANCE_TEXT,
        }
    return {
        "Recommendation": role,
        "Supplier": winner["supplier_name"],
        "Explanation": RECOMMENDATION_EXPLANATIONS[role],
        "Evidence Status": evidence_status,
        "Confidence": confidence,
        "Human Review Status": "Required",
        "Trade-Off": "This role-specific recommendation remains subject to commercial, legal, quality, compliance, and governance approval.",
        "Qualification Condition": condition,
        "Governance": GOVERNANCE_TEXT,
    }


def generate_supplier_recommendations(profiles):
    suppliers = [_flat(profile) for profile in profiles]
    results = []

    exit_candidate = min(suppliers, key=lambda x: x["supplier360"])
    exit_name = exit_candidate["supplier_name"]
    non_exit = [x for x in suppliers if x["supplier_name"] != exit_name]

    best_value = max(suppliers, key=lambda x: x["supplier360"] * 0.45 + x["performance"] * 0.25 + x["strategic"] * 0.20 + x["financial"] * 0.10)
    results.append(_result("Best Value Supplier", best_value, "Governed scores used"))
    results.append(_result("Lowest Cost Supplier", min(suppliers, key=lambda x: x["price"] if x["price"] else float("inf")), "Commercial data supplied"))
    results.append(_result("Lowest Risk Supplier", max(suppliers, key=lambda x: x["risk"] * 0.5 + x["financial"] * 0.25 + x["performance"] * 0.25), "Governed scores used"))
    results.append(_result("Best Performer", max(suppliers, key=lambda x: x["performance"]), "Operational evidence available"))

    qualified_innovation = [x for x in non_exit if x["innovation_status"] != "Insufficient Data" and x["innovation_completeness"] >= 40 and x["classification"] != "Exit Candidate"]
    results.append(_result("Most Innovative Supplier", max(qualified_innovation, key=lambda x: x["innovation"]) if qualified_innovation else None, "Verified innovation evidence required", condition="Innovation completeness must be at least 40%."))

    qualified_esg = [x for x in non_exit if x["esg_status"] != "Insufficient Data" and x["esg_completeness"] >= 40 and x["classification"] != "Exit Candidate"]
    results.append(_result("Most Sustainable Supplier", max(qualified_esg, key=lambda x: x["esg"]) if qualified_esg else None, "Verified ESG evidence required", condition="ESG completeness must be at least 40%."))

    strategic_candidates = [x for x in non_exit if x["classification"] != "Exit Candidate" and x["financial_status"] != "Insufficient Data"]
    results.append(_result("Best Strategic Partner", max(strategic_candidates, key=lambda x: x["strategic"]) if strategic_candidates else None, "Financial and strategic evidence required", condition="Supplier cannot be an Exit Candidate and must have sufficient financial evidence."))

    long_term_candidates = [x for x in strategic_candidates if x["esg_status"] != "Insufficient Data" and x["innovation_status"] != "Insufficient Data"]
    long_term = max(long_term_candidates, key=lambda x: x["supplier360"] * 0.30 + x["financial"] * 0.20 + x["performance"] * 0.20 + x["esg"] * 0.10 + x["innovation"] * 0.10 + x["strategic"] * 0.10) if long_term_candidates else None
    results.append(_result("Best Long-Term Supplier", long_term, "Multi-dimensional evidence required", condition="Financial, ESG, and innovation evidence must be sufficient."))

    results.append(_result("Exit Candidate", exit_candidate, "Lowest governed Supplier 360 profile", condition="Corrective-action and governance review required."))
    development = min(non_exit, key=lambda x: abs(x["supplier360"] - 55)) if non_exit else None
    results.append(_result("Development Candidate", development, "Capability-development opportunity", condition="Development plan required before strategic award."))

    return results


def generate_executive_supplier_narrative(profiles, recommendations):
    best = next(item for item in recommendations if item["Recommendation"] == "Best Value Supplier")
    if best["Supplier"] == "No Qualified Supplier":
        return "No supplier currently qualifies for a final Best Value recommendation. Close evidence and governance gaps before award review."
    profile = next(item for item in profiles if item["supplier_name"] == best["Supplier"])
    alternatives = [item["supplier_name"] for item in profiles if item["supplier_name"] != best["Supplier"]]
    return (
        f"SUPPLIER LANDSCAPE\n{len(profiles)} suppliers were assessed using governed performance, risk resilience, financial, ESG, innovation, and relationship indicators.\n\n"
        f"RECOMMENDATION\n{best['Supplier']} is the current Best Value Supplier, subject to validation status and human approval.\n\n"
        f"WHY SELECTED\nSupplier 360 {profile['overall_supplier360_score']}/100; performance {profile['performance']['overall_supplier_performance_score']}/100; governed financial indicator {profile['financial'].get('displayed_financial_score', 0)}/100; governed ESG {profile['esg'].get('displayed_esg_score', 0)}/100; governed innovation {profile['innovation'].get('displayed_innovation_score', 0)}/100.\n\n"
        f"ALTERNATIVES\n{', '.join(alternatives) or 'No alternative supplier'} remain relevant for competition, continuity, development, or specialist roles.\n\n"
        f"NEXT STEPS\nValidate capacity, normalize commercial terms, close evidence gaps, and document human approval."
    )
