"""Streamlit UI for Supplier Intelligence Platform."""

import pandas as pd
import streamlit as st


def render_supplier_intelligence(intelligence):
    st.header("Supplier Intelligence")
    comparison = intelligence["comparison_df"]
    profiles = intelligence["profiles"]
    recommendations = pd.DataFrame(intelligence["recommendations"])

    st.subheader("Supplier Comparison")
    st.dataframe(comparison, width="stretch", hide_index=True)

    st.subheader("Recommendation Rankings")
    st.dataframe(recommendations, width="stretch", hide_index=True)

    supplier_names = [profile["supplier_name"] for profile in profiles]
    selected = st.selectbox("Select Supplier 360 Profile", supplier_names, index=0)
    profile = next(item for item in profiles if item["supplier_name"] == selected)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Supplier 360", f"{profile['overall_supplier360_score']}/100")
    c2.metric("Performance", f"{profile['performance']['overall_supplier_performance_score']}/100")
    c3.metric("ESG Maturity", profile["esg"]["esg_maturity_level"])
    c4.metric("SRM Class", profile["srm"]["srm_classification"])

    st.subheader("Supplier 360 Profile")
    overview = {
        "Supplier": profile["supplier_name"],
        "Type": profile["supplier_type"],
        "Country": profile["country"],
        "Manufacturing Location": profile["manufacturing_location"],
        "Annual Capacity": profile["annual_capacity"],
        "Capacity Utilization %": profile["capacity_utilization"],
        "Approved Categories": profile["approved_categories"],
        "Commodity Coverage": profile["commodity_coverage"],
        "Qualification Status": profile["qualification_status"],
        "Audit Status": profile["audit_status"],
        "Contract Status": profile["contract_status"],
        "Relationship Owner": profile["relationship_owner"],
    }
    st.dataframe(pd.DataFrame([overview]), width="stretch", hide_index=True)
    if profile["defaults_used"]:
        st.warning("Defaulted or unavailable fields: " + ", ".join(profile["defaults_used"]))

    tabs = st.tabs(["Performance", "Financial", "ESG", "Innovation", "SRM"])
    with tabs[0]:
        st.json(profile["performance"])
    with tabs[1]:
        st.json(profile["financial"])
    with tabs[2]:
        st.json(profile["esg"])
    with tabs[3]:
        st.json(profile["innovation"])
    with tabs[4]:
        st.json(profile["srm"])

    st.subheader("Executive Supplier Narrative")
    st.text_area("Procurement Director review narrative", intelligence["executive_narrative"], height=520)
    st.success("Transparent, rule-guided, auditable, and not black-box AI. Human approval remains mandatory.")
