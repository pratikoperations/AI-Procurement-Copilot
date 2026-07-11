"""Supplier Intelligence orchestration and side-by-side comparison."""

import pandas as pd

from modules.supplier360_engine import build_supplier360_profiles
from modules.supplier_recommendation_engine import generate_executive_supplier_narrative, generate_supplier_recommendations


def build_supplier_intelligence(scored_df, category, commodity):
    profiles = build_supplier360_profiles(scored_df, category, commodity)
    source_rows = {row["Supplier"]: row for _, row in scored_df.iterrows()}
    for profile in profiles:
        row = source_rows[profile["supplier_name"]]
        profile["quoted_price"] = float(row.get("Quoted Unit Price USD", 0))
        profile["adjusted_tco"] = float(row.get("adjusted_tco_unit_usd", 0))
        profile["risk_score"] = float(row.get("risk_score", 60))
        profile["lead_time"] = float(row.get("Lead Time Days", 0))
        profile["moq"] = float(row.get("MOQ", 0))
        profile["payment_terms"] = str(row.get("Payment Terms", "Not provided"))
        profile["capacity"] = float(row.get("Supplier Capacity", profile["annual_capacity"]))

    recommendations = generate_supplier_recommendations(profiles)
    status_map = {}
    for rec in recommendations:
        status_map.setdefault(rec["Supplier"], []).append(rec["Recommendation"])

    rows = []
    for profile in profiles:
        rows.append({
            "Supplier": profile["supplier_name"],
            "Quoted Price USD": profile["quoted_price"],
            "Risk-Adjusted TCO USD": profile["adjusted_tco"],
            "Risk Score": profile["risk_score"],
            "Performance Score": profile["performance"]["overall_supplier_performance_score"],
            "ESG Score": profile["esg"]["esg_maturity_score"],
            "Innovation Score": profile["innovation"]["innovation_score"],
            "Financial Health Score": profile["financial"]["financial_stability_score"],
            "Capacity": profile["capacity"],
            "Lead Time Days": profile["lead_time"],
            "MOQ": profile["moq"],
            "Payment Terms": profile["payment_terms"],
            "SRM Classification": profile["srm"]["srm_classification"],
            "Supplier 360 Score": profile["overall_supplier360_score"],
            "Recommendation Status": "; ".join(status_map.get(profile["supplier_name"], ["Qualified for comparison"])),
        })
    comparison = pd.DataFrame(rows).sort_values("Supplier 360 Score", ascending=False).reset_index(drop=True)
    narrative = generate_executive_supplier_narrative(profiles, recommendations)
    return {"profiles": profiles, "comparison_df": comparison, "recommendations": recommendations, "executive_narrative": narrative}
