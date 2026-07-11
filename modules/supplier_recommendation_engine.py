"""Explainable supplier recommendation rankings."""


def _winner(profiles, key, reverse=True):
    return sorted(profiles, key=lambda item: item[key], reverse=reverse)[0]


def generate_supplier_recommendations(profiles):
    enriched = []
    for profile in profiles:
        flat = {
            "supplier_name": profile["supplier_name"],
            "supplier360": profile["overall_supplier360_score"],
            "performance": profile["performance"]["overall_supplier_performance_score"],
            "financial": profile["financial"]["financial_stability_score"],
            "esg": profile["esg"]["esg_maturity_score"],
            "innovation": profile["innovation"]["innovation_score"],
            "strategic": profile["srm"]["strategic_index"],
            "risk": float(profile.get("risk_score", profile.get("performance", {}).get("risk_score", 60))),
            "price": float(profile.get("quoted_price", 0)),
            "tco": float(profile.get("adjusted_tco", 0)),
            "classification": profile["srm"]["srm_classification"],
        }
        enriched.append(flat)

    categories = {
        "Best Value Supplier": (lambda x: x["supplier360"] * 0.45 + x["performance"] * 0.25 + x["strategic"] * 0.20 + x["financial"] * 0.10, True),
        "Lowest Cost Supplier": (lambda x: -x["price"] if x["price"] else x["supplier360"], True),
        "Lowest Risk Supplier": (lambda x: x["financial"] * 0.45 + x["performance"] * 0.35 + x["supplier360"] * 0.20, True),
        "Best Performer": (lambda x: x["performance"], True),
        "Most Innovative Supplier": (lambda x: x["innovation"], True),
        "Most Sustainable Supplier": (lambda x: x["esg"], True),
        "Best Strategic Partner": (lambda x: x["strategic"], True),
        "Best Long-Term Supplier": (lambda x: x["supplier360"] * 0.35 + x["financial"] * 0.25 + x["performance"] * 0.20 + x["esg"] * 0.10 + x["innovation"] * 0.10, True),
        "Development Candidate": (lambda x: -abs(x["supplier360"] - 55), True),
        "Exit Candidate": (lambda x: -x["supplier360"], True),
    }
    results = []
    for label, (scorer, reverse) in categories.items():
        ranked = sorted(enriched, key=scorer, reverse=reverse)
        winner = ranked[0]
        results.append({
            "Recommendation": label,
            "Supplier": winner["supplier_name"],
            "Score Basis": round(float(scorer(winner)),1),
            "Explanation": f"Selected using deterministic comparison of Supplier 360, performance, financial health, ESG, innovation, and SRM factors relevant to {label.lower()}.",
            "Trade-Off": "Recommendation is role-specific and does not replace final commercial, legal, quality, or governance approval.",
            "Governance": "Transparent, rule-guided, auditable, and not black-box AI.",
        })
    return results


def generate_executive_supplier_narrative(profiles, recommendations):
    best = next(item for item in recommendations if item["Recommendation"] == "Best Value Supplier")
    profile = next(item for item in profiles if item["supplier_name"] == best["Supplier"])
    alternatives = [item["supplier_name"] for item in profiles if item["supplier_name"] != best["Supplier"]]
    return (
        f"SUPPLIER LANDSCAPE\n{len(profiles)} suppliers were assessed across performance, risk signals, financial health indicators, ESG maturity, innovation, and relationship fit.\n\n"
        f"RECOMMENDATION\n{best['Supplier']} is the Best Value Supplier with Supplier 360 score {profile['overall_supplier360_score']}/100 and SRM classification {profile['srm']['srm_classification']}.\n\n"
        f"WHY SELECTED\nPerformance {profile['performance']['overall_supplier_performance_score']}/100; financial health indicator {profile['financial']['financial_stability_score']}/100; ESG maturity {profile['esg']['esg_maturity_score']}/100; innovation {profile['innovation']['innovation_score']}/100.\n\n"
        f"ALTERNATIVES\n{', '.join(alternatives) or 'No alternative supplier'} remain relevant for competition, continuity, development, or specialist roles but did not lead the combined Supplier 360 assessment.\n\n"
        f"RELATIONSHIP STRATEGY\n{profile['srm']['relationship_strategy']}\n\n"
        f"DEVELOPMENT PRIORITIES\n{' '.join(profile['performance']['supplier_development_actions'])}\n\n"
        f"FINANCIAL AND ESG CONTROLS\n{profile['financial']['disclaimer']} Complete required ESG evidence and due diligence before final award.\n\n"
        f"NEXT STEPS\nValidate capacity, confirm commercial terms, close data gaps, agree governance cadence, and document human approval."
    )
