"""Supplier Intelligence orchestration and executive-readable comparison."""

import pandas as pd

from modules.c1_ux import technical_eligibility_label
from modules.supplier360_engine import build_supplier360_profiles
from modules.supplier_recommendation_engine import generate_executive_supplier_narrative, generate_supplier_recommendations


def build_supplier_intelligence(scored_df, category, commodity):
    profiles=build_supplier360_profiles(scored_df,category,commodity)
    source_rows={row["Supplier"]:row for _,row in scored_df.iterrows()}
    governed_score_map={}
    for profile in profiles:
        row=source_rows[profile["supplier_name"]]
        profile.update({
            "quoted_price":float(row.get("Quoted Unit Price USD",0)),
            "adjusted_tco":float(row.get("adjusted_tco_unit_usd",0)),
            "risk_score":float(row.get("risk_score",60)),
            "risk_category":str(row.get("risk_category",row.get("Risk Category","Not assessed"))),
            "failure_probability":float(row.get("failure_probability",0)),
            "technical_eligibility":technical_eligibility_label(row.get("technical_eligible")),
            "technical_ineligibility_reasons":"; ".join(row.get("technical_ineligibility_reasons",[]) or []),
            "lead_time":float(row.get("Lead Time Days",0)),"moq":float(row.get("MOQ",0)),
            "payment_terms":str(row.get("Payment Terms","Not provided")),
            "capacity":float(row.get("Supplier Capacity",profile["annual_capacity"])),
            "original_currency":str(row.get("Original Currency",row.get("Currency","USD"))),
            "original_unit_price":float(row.get("Original Unit Price",row.get("Quoted Unit Price USD",0))),
            "normalized_currency":str(row.get("Normalized Currency","USD")),
            "normalized_unit_price":float(row.get("Normalized Unit Price",row.get("Quoted Unit Price USD",0))),
            "fx_rate_used":row.get("FX Rate Used",1.0),
            "unit_of_measure":str(row.get("Unit of Measure",row.get("Unit","Not provided"))),
        })
        profile["comparison_basis"]=str(row.get("Comparison Basis",f"{profile['normalized_currency']} per {profile['unit_of_measure']}"))
        governed_score_map[profile["supplier_name"]]={
            "supplier360_performance_score":profile["performance"].get("overall_supplier_performance_score",0),
            "governed_financial_indicator":profile["financial"].get("displayed_financial_score",profile["financial"].get("financial_stability_score",0)),
            "governed_esg_maturity_score":profile["esg"].get("displayed_esg_score",profile["esg"].get("esg_maturity_score",0)),
            "governed_innovation_maturity_score":profile["innovation"].get("displayed_innovation_score",profile["innovation"].get("innovation_score",0)),
            "supplier360_score":profile.get("overall_supplier360_score",0),
        }
    for column in ["supplier360_performance_score","governed_financial_indicator","governed_esg_maturity_score","governed_innovation_maturity_score","supplier360_score"]:
        scored_df[column]=scored_df["Supplier"].map(lambda supplier:governed_score_map.get(supplier,{}).get(column,0))
    recommendations=generate_supplier_recommendations(profiles)
    status_map={}
    for rec in recommendations:
        supplier=rec.get("Supplier")
        if supplier and supplier!="No Qualified Supplier": status_map.setdefault(supplier,[]).append(rec["Recommendation"])
    rows=[]
    for profile in profiles:
        financial,esg,innovation=profile["financial"],profile["esg"],profile["innovation"]
        rows.append({
            "Supplier":profile["supplier_name"],"Technical Eligibility":profile["technical_eligibility"],
            "Technical Ineligibility Reasons":profile["technical_ineligibility_reasons"] or "None",
            "Original Currency":profile["original_currency"],"Original Unit Price":profile["original_unit_price"],
            "Normalized Currency":profile["normalized_currency"],"Normalized Unit Price":profile["normalized_unit_price"],
            "FX Rate Used":profile["fx_rate_used"],"Unit of Measure":profile["unit_of_measure"],"Comparison Basis":profile["comparison_basis"],
            "Risk-Adjusted TCO (USD)":profile["adjusted_tco"],"Risk Resilience Score":profile["risk_score"],
            "Risk Category":profile["risk_category"],"Failure Probability":profile["failure_probability"],
            "Performance Score":profile["performance"]["overall_supplier_performance_score"],
            "Financial Assessment":financial.get("assessment_status","Not assessed"),"Financial Indicator":financial.get("displayed_financial_score",financial.get("financial_stability_score",0)),
            "ESG Assessment":esg.get("assessment_status","Not assessed"),"ESG Maturity":esg.get("esg_maturity_level","Not assessed"),"ESG Score":esg.get("displayed_esg_score",esg.get("esg_maturity_score",0)),
            "Innovation Assessment":innovation.get("assessment_status","Not assessed"),"Innovation Maturity":innovation.get("innovation_maturity_level","Not assessed"),"Innovation Score":innovation.get("displayed_innovation_score",innovation.get("innovation_score",0)),
            "Capacity":profile["capacity"],"Lead Time Days":profile["lead_time"],"MOQ":profile["moq"],"Payment Terms":profile["payment_terms"],
            "SRM Classification":profile["srm"]["srm_classification"],"Supplier 360 Score":profile["overall_supplier360_score"],
            "Recommendation Status":"; ".join(status_map.get(profile["supplier_name"],["Qualified for comparison"])),
        })
    comparison=pd.DataFrame(rows).sort_values(["Technical Eligibility","Supplier 360 Score"],ascending=[False,False]).reset_index(drop=True)
    narrative=generate_executive_supplier_narrative(profiles,recommendations)
    return {"profiles":profiles,"comparison_df":comparison,"recommendations":recommendations,"executive_narrative":narrative}
