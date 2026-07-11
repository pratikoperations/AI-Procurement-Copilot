"""Supplier Intelligence orchestration and executive-readable comparison."""

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
        profile["original_currency"] = str(row.get("Original Currency", row.get("Currency", "USD")))
        profile["original_unit_price"] = float(row.get("Original Unit Price", row.get("Quoted Unit Price USD", 0)))
        profile["normalized_currency"] = str(row.get("Normalized Currency", "USD"))
        profile["normalized_unit_price"] = float(row.get("Normalized Unit Price", row.get("Quoted Unit Price USD", 0)))
        profile["fx_rate_used"] = row.get("FX Rate Used", 1.0)
        profile["unit_of_measure"] = str(row.get("Unit of Measure", row.get("Unit", "Not provided")))
        profile["comparison_basis"] = str(row.get("Comparison Basis", f"{profile['normalized_currency']} per {profile['unit_of_measure']}"))

    recommendations = generate_supplier_recommendations(profiles)
    status_map = {}
    for rec in recommendations:
        supplier = rec.get("Supplier")
        if supplier and supplier != "No Qualified Supplier":
            status_map.setdefault(supplier, []).append(rec["Recommendation"])

    rows = []
    for profile in profiles:
        financial = profile["financial"]
        esg = profile["esg"]
        innovation = profile["innovation"]
        rows.append({
            "Supplier": profile["supplier_name"],
            "Original Currency": profile["original_currency"],
            "Original Unit Price": profile["original_unit_price"],
            "Normalized Currency": profile["normalized_currency"],
            "Normalized Unit Price": profile["normalized_unit_price"],
            "FX Rate Used": profile["fx_rate_used"],
            "Unit of Measure": profile["unit_of_measure"],
            "Comparison Basis": profile["comparison_basis"],
            "Risk-Adjusted TCO (USD)": profile["adjusted_tco"],
            "Risk Resilience Score": profile["risk_score"],
            "Performance Score": profile["performance"]["overall_supplier_performance_score"],
            "Financial Assessment": financial.get("assessment_status", "Not assessed"),
            "Financial Indicator": financial.get("displayed_financial_score", financial.get("financial_stability_score", 0)),
            "ESG Assessment": esg.get("assessment_status", "Not assessed"),
            "ESG Maturity": esg.get("esg_maturity_level", "Not assessed"),
            "ESG Score": esg.get("displayed_esg_score", esg.get("esg_maturity_score", 0)),
            "Innovation Assessment": innovation.get("assessment_status", "Not assessed"),
            "Innovation Maturity": innovation.get("innovation_maturity_level", "Not assessed"),
            "Innovation Score": innovation.get("displayed_innovation_score", innovation.get("innovation_score", 0)),
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
