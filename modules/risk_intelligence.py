"""Procurement risk intelligence and mitigation recommendations."""

SEVERITY_ORDER = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}


def _severity(score):
    if score >= 80:
        return "Critical"
    if score >= 60:
        return "High"
    if score >= 35:
        return "Medium"
    return "Low"


def assess_procurement_risks(scored_df, allocation_df=None):
    risks = []
    top = scored_df.iloc[0]

    concentration = 100.0
    if allocation_df is not None and not allocation_df.empty:
        concentration = float(allocation_df["Recommended Allocation %"].max())
    risks.append({
        "Risk": "Supply concentration",
        "Severity": _severity(concentration),
        "Evidence": f"Largest recommended supplier share is {concentration:.0f}%.",
        "Mitigation": "Retain a qualified backup supplier and define contingency allocation triggers.",
    })

    lead_days = float(top.get("Lead Time Days", 0))
    risks.append({
        "Risk": "Logistics risk",
        "Severity": _severity(min(100, lead_days * 2.5)),
        "Evidence": f"Recommended supplier lead time is {lead_days:.0f} days.",
        "Mitigation": "Set lead-time SLA, safety-stock logic, and escalation triggers.",
    })

    capacity_buffer = float(top.get("Capacity Buffer %", 10))
    risks.append({
        "Risk": "Capacity risk",
        "Severity": _severity(max(0, 90 - capacity_buffer * 4)),
        "Evidence": f"Reported capacity buffer is {capacity_buffer:.1f}%.",
        "Mitigation": "Validate available capacity and secure reserved capacity in contract.",
    })

    esg_score = float(top.get("esg_score", 50))
    risks.append({
        "Risk": "ESG risk",
        "Severity": _severity(max(0, 100 - esg_score)),
        "Evidence": f"ESG score is {esg_score:.1f}/100.",
        "Mitigation": "Close documentation gaps and agree corrective-action milestones.",
    })

    quality_ppm = float(top.get("Quality PPM", 1000))
    risks.append({
        "Risk": "Quality risk",
        "Severity": _severity(min(100, quality_ppm / 20)),
        "Evidence": f"Quality performance is {quality_ppm:.0f} PPM.",
        "Mitigation": "Set PPM targets, incoming-quality controls, and chargeback clauses.",
    })

    currency = str(top.get("Currency", "USD")).upper()
    risks.append({
        "Risk": "Currency risk",
        "Severity": "Medium" if currency not in {"INR", "LOCAL"} else "Low",
        "Evidence": f"Quote currency is {currency}.",
        "Mitigation": "Use FX adjustment bands, hedging policy, or local-currency quotation where practical.",
    })

    risks.extend([
        {"Risk": "Country risk", "Severity": "Low", "Evidence": "Country-level external data is not supplied.", "Mitigation": "Complete country-risk review before final award."},
        {"Risk": "Geographic risk", "Severity": "Low", "Evidence": "Plant/location diversification data is limited.", "Mitigation": "Confirm manufacturing site and alternate-site capability."},
        {"Risk": "Financial risk", "Severity": "Medium", "Evidence": "Financial health data is not included in the RFQ.", "Mitigation": "Complete credit and financial due diligence before contracting."},
    ])

    risks = sorted(risks, key=lambda item: SEVERITY_ORDER[item["Severity"]], reverse=True)
    highest = risks[0]["Severity"] if risks else "Low"
    return {
        "risks": risks,
        "highest_severity": highest,
        "top_mitigation": risks[0]["Mitigation"] if risks else "No mitigation required.",
        "critical_count": sum(item["Severity"] == "Critical" for item in risks),
        "high_count": sum(item["Severity"] == "High" for item in risks),
    }
