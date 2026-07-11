"""Executive-readable Streamlit UI for Supplier Intelligence Platform."""

import pandas as pd
import streamlit as st

from modules.ui_components import (
    build_readable_supplier_report,
    humanize_label,
    render_action_plan,
    render_comparison_matrix,
    render_data_completeness_card,
    render_dimension_chart,
    render_evidence_list,
    render_executive_summary_card,
    render_gaps_panel,
    render_governance_note,
    render_key_value_matrix,
    render_risk_alert,
    render_score_matrix,
    render_status_badge,
    render_strengths_panel,
)


def _readable_recommendations(recommendations):
    frame = pd.DataFrame(recommendations)
    if frame.empty:
        return frame
    rename_map = {column: humanize_label(column) for column in frame.columns}
    rename_map.update({
        "Recommendation": "Recommendation Role",
        "Supplier": "Recommended Supplier",
        "Rationale": "Business Rationale",
        "Trade Off": "Main Trade-Off",
        "Trade-off": "Main Trade-Off",
    })
    frame = frame.rename(columns=rename_map)
    preferred = [
        "Recommendation Role", "Recommended Supplier", "Business Rationale",
        "Main Strength", "Main Trade-Off", "Confidence", "Human Review Status",
    ]
    available = [column for column in preferred if column in frame.columns]
    remaining = [column for column in frame.columns if column not in available and "score basis" not in column.lower()]
    return frame[available + remaining]


def _readable_comparison(comparison):
    frame = comparison.copy()
    rename = {
        "Quoted Price USD": "Quoted Price (USD)",
        "Risk-Adjusted TCO USD": "Risk-Adjusted TCO (USD)",
        "Financial Health Score": "Financial Indicator",
        "ESG Score": "ESG Maturity Score",
        "Innovation Score": "Innovation Maturity Score",
    }
    return frame.rename(columns=rename)


def _render_performance(performance):
    render_status_badge("Performance category", performance.get("performance_category", "Not assessed"))
    render_score_matrix({
        "Overall performance": performance.get("overall_supplier_performance_score", 0),
        "Quality": performance.get("quality_score", 0),
        "Delivery": performance.get("delivery_score", 0),
        "Service": performance.get("service_score", 0),
        "Commercial": performance.get("commercial_score", 0),
        "Improvement": performance.get("improvement_score", 0),
    })
    render_dimension_chart("Performance dimension scores", {
        "Quality": performance.get("quality_score", 0),
        "Delivery": performance.get("delivery_score", 0),
        "Service": performance.get("service_score", 0),
        "Commercial": performance.get("commercial_score", 0),
        "Improvement": performance.get("improvement_score", 0),
    })
    c1, c2 = st.columns(2)
    with c1:
        render_strengths_panel(performance.get("key_strengths", []))
    with c2:
        render_gaps_panel(performance.get("key_weaknesses", []))
    render_action_plan(performance.get("supplier_development_actions", []), cadence="Quarterly supplier review")


def _render_financial(financial):
    render_status_badge("Assessment status", financial.get("assessment_status", "Not assessed"), financial.get("confidence_warning"))
    render_data_completeness_card(
        financial.get("data_completeness_score", 0),
        financial.get("assessment_status", "Not assessed"),
        financial.get("evidence_quality", "Not assessed"),
    )
    render_score_matrix({"Displayed financial indicator": financial.get("displayed_financial_score", financial.get("financial_stability_score", 0))})
    render_key_value_matrix("Risk indicators", {
        "Financial risk category": financial.get("financial_risk_category", "Not assessed"),
        "Dependency risk": financial.get("dependency_risk", "Not assessed"),
        "Working capital risk": financial.get("working_capital_risk", "Not assessed"),
        "Capacity stress": financial.get("capacity_stress_indicator", "Not assessed"),
        "Due diligence required": "Yes" if financial.get("due_diligence_required", True) else "No",
    })
    render_evidence_list(financial.get("evidence", []))
    render_action_plan(financial.get("due_diligence_actions", []), owner="Finance, procurement and risk", cadence="Before award approval")
    render_risk_alert(
        "Mandatory financial disclaimer",
        financial.get("disclaimer", "Financial outputs are indicators only and require due diligence."),
        "warning",
    )


def _render_esg(esg):
    render_status_badge("Assessment status", esg.get("assessment_status", "Not assessed"))
    render_data_completeness_card(esg.get("esg_data_completeness", 0), esg.get("assessment_status", "Not assessed"), esg.get("evidence_quality", "Not assessed"))
    render_score_matrix({
        "Displayed ESG maturity": esg.get("displayed_esg_score", esg.get("esg_maturity_score", 0)),
        "Environmental": esg.get("environmental_score", 0),
        "Social": esg.get("social_score", 0),
        "Governance": esg.get("governance_score", 0),
    })
    render_status_badge("ESG maturity level", esg.get("esg_maturity_level", "Not assessed"))
    render_dimension_chart("ESG dimension scores", {
        "Environmental": esg.get("environmental_score", 0),
        "Social": esg.get("social_score", 0),
        "Governance": esg.get("governance_score", 0),
    })
    c1, c2 = st.columns(2)
    with c1:
        render_strengths_panel(esg.get("esg_strengths", []))
    with c2:
        render_gaps_panel(esg.get("esg_gaps", []))
    st.markdown("#### Required documentation")
    for item in esg.get("required_documentation", []):
        st.checkbox(str(item), value=False, disabled=True, key=f"esg_doc_{id(esg)}_{item}")
    render_action_plan(esg.get("corrective_actions", []), owner="Sustainability and supplier owner", cadence="Next ESG review")
    if esg.get("verification_required", True):
        render_risk_alert("Verification required", "ESG conclusions remain provisional until supporting evidence is verified.")


def _render_innovation(innovation):
    render_status_badge("Assessment status", innovation.get("assessment_status", "Not assessed"))
    render_data_completeness_card(innovation.get("innovation_data_completeness", 0), innovation.get("assessment_status", "Not assessed"), innovation.get("evidence_quality", "Not assessed"))
    render_score_matrix({"Displayed innovation maturity": innovation.get("displayed_innovation_score", innovation.get("innovation_score", 0))})
    render_status_badge("Innovation maturity", innovation.get("innovation_maturity_level", "Not assessed"))
    render_dimension_chart("Innovation capability scores", innovation.get("innovation_dimensions", {}))
    c1, c2 = st.columns(2)
    with c1:
        render_strengths_panel(innovation.get("innovation_strengths", []))
    with c2:
        render_gaps_panel(innovation.get("innovation_gaps", []))
    opportunities = []
    for index, item in enumerate(innovation.get("collaboration_opportunities", []), start=1):
        opportunities.append({
            "Priority": index,
            "Opportunity": item,
            "Business value": "Validate through a joint business case",
            "Effort": "Medium",
            "Suggested next step": "Assign an owner and define a measurable pilot",
        })
    if opportunities:
        render_comparison_matrix(pd.DataFrame(opportunities), "Collaboration opportunities")
    render_executive_summary_card("Recommended innovation agenda", innovation.get("recommended_innovation_agenda", "No agenda generated."))


def _render_srm(srm):
    render_status_badge("SRM classification", srm.get("srm_classification", "Not assessed"))
    render_score_matrix({"Strategic index": srm.get("strategic_index", 0)})
    render_key_value_matrix("Relationship governance", {
        "Relationship intensity": srm.get("relationship_intensity", "Not assessed"),
        "Governance cadence": srm.get("governance_cadence", "Not assessed"),
        "Executive sponsor required": "Yes" if srm.get("executive_sponsor_required") else "No",
        "Review frequency": srm.get("review_frequency", "Not assessed"),
        "Spend classification": srm.get("spend_classification", "Not assessed"),
    })
    render_executive_summary_card("Classification rationale", srm.get("classification_rationale", "No rationale generated."))
    render_executive_summary_card("Recommended relationship strategy", srm.get("relationship_strategy", "No strategy generated."))
    governance = pd.DataFrame([{
        "Governance level": srm.get("relationship_intensity", "Not assessed"),
        "Meeting cadence": srm.get("governance_cadence", "Not assessed"),
        "Participants": "Procurement, business owner and supplier leadership",
        "Decision rights": "Human procurement governance",
        "Escalation path": "Category lead to procurement director",
        "Performance review": srm.get("review_frequency", "Not assessed"),
    }])
    render_comparison_matrix(governance, "Governance matrix")


def render_supplier_intelligence(intelligence):
    st.header("Supplier Intelligence")
    comparison = _readable_comparison(intelligence["comparison_df"])
    profiles = intelligence["profiles"]
    recommendations = _readable_recommendations(intelligence["recommendations"])

    render_comparison_matrix(comparison, "Executive supplier comparison")
    if not recommendations.empty:
        render_comparison_matrix(recommendations, "Recommendation rankings")

    supplier_names = [profile["supplier_name"] for profile in profiles]
    selected = st.selectbox("Select Supplier 360 Profile", supplier_names, index=0)
    profile = next(item for item in profiles if item["supplier_name"] == selected)
    performance = profile.get("performance", {})
    financial = profile.get("financial", {})
    esg = profile.get("esg", {})
    innovation = profile.get("innovation", {})
    srm = profile.get("srm", {})

    st.subheader("Executive overview")
    c1, c2, c3 = st.columns(3)
    c1.metric("Supplier 360", f"{profile.get('overall_supplier360_score', 0)}/100")
    c2.metric("Performance", f"{performance.get('overall_supplier_performance_score', 0)}/100")
    c3.metric("Recommendation status", next((row.get("Recommendation Status") for _, row in comparison.iterrows() if row.get("Supplier") == selected), "Qualified for comparison"))
    c4, c5, c6 = st.columns(3)
    c4.metric("Financial assessment", financial.get("assessment_status", "Not assessed"))
    c5.metric("ESG maturity", esg.get("esg_maturity_level", "Not assessed"))
    c6.metric("Innovation maturity", innovation.get("innovation_maturity_level", "Not assessed"))
    c7, c8 = st.columns(2)
    c7.metric("SRM classification", srm.get("srm_classification", "Not assessed"))
    c8.metric("Financial data completeness", f"{financial.get('data_completeness_score', 0):.1f}%")

    render_dimension_chart("Supplier intelligence dimensions", {
        "Performance": performance.get("overall_supplier_performance_score", 0),
        "Financial": financial.get("displayed_financial_score", financial.get("financial_stability_score", 0)),
        "ESG": esg.get("displayed_esg_score", esg.get("esg_maturity_score", 0)),
        "Innovation": innovation.get("displayed_innovation_score", innovation.get("innovation_score", 0)),
        "Strategic fit": srm.get("strategic_index", 0),
        "Risk strength": profile.get("risk_score", 0),
    })

    st.subheader("Supplier 360 profile")
    render_key_value_matrix("Supplier identity", {
        "Supplier name": profile.get("supplier_name"),
        "Supplier type": profile.get("supplier_type"),
        "Country": profile.get("country"),
        "Manufacturing location": profile.get("manufacturing_location"),
        "Manufacturing footprint": profile.get("manufacturing_footprint"),
    })
    render_key_value_matrix("Commercial position", {
        "Spend classification": profile.get("spend_classification"),
        "Preferred supplier status": profile.get("preferred_supplier_status"),
        "Contract status": profile.get("contract_status"),
        "Approved categories": ", ".join(map(str, profile.get("approved_categories", []))),
        "Commodity coverage": ", ".join(map(str, profile.get("commodity_coverage", []))),
    })
    render_key_value_matrix("Capacity and continuity", {
        "Annual capacity": profile.get("annual_capacity"),
        "Capacity utilization": f"{profile.get('capacity_utilization', 0)}%",
        "Supplier dependency": profile.get("supplier_dependency"),
        "Business continuity status": profile.get("business_continuity_status"),
        "Qualification status": profile.get("qualification_status"),
        "Audit status": profile.get("audit_status"),
    })
    render_key_value_matrix("Relationship governance", {
        "Relationship owner": profile.get("relationship_owner"),
        "Strategic importance": profile.get("strategic_importance"),
        "SRM classification": srm.get("srm_classification"),
        "Review cadence": srm.get("review_frequency"),
    })
    if profile.get("defaults_used"):
        render_risk_alert("Defaulted or unavailable fields", ", ".join(humanize_label(item) for item in profile.get("defaults_used", [])))

    tabs = st.tabs(["Performance", "Financial", "ESG", "Innovation", "SRM"])
    with tabs[0]:
        _render_performance(performance)
    with tabs[1]:
        _render_financial(financial)
    with tabs[2]:
        _render_esg(esg)
    with tabs[3]:
        _render_innovation(innovation)
    with tabs[4]:
        _render_srm(srm)

    render_executive_summary_card("Executive supplier narrative", intelligence["executive_narrative"])
    readable_report = build_readable_supplier_report(profile)
    st.download_button("Download Supplier 360 Readable Report", readable_report.encode("utf-8"), f"{selected.replace(' ', '_').lower()}_supplier360_report.txt", "text/plain")
    render_governance_note("Transparent, rule-guided, auditable, and not black-box AI. Human approval remains mandatory.")
