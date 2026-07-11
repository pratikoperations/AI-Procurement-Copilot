"""AI Procurement Copilot — Portfolio Edition v1.0."""

import streamlit as st

from modules.allocation import recommend_allocation
from modules.allocation_optimizer import optimize_allocation
from modules.category_cost_router import calculate_category_should_cost
from modules.category_engine import ensure_category_profile
from modules.config import APP_NAME, BUILD, EDITION, STATUS
from modules.data_loader import get_demo_data, load_uploaded_rfq
from modules.dashboard import (
    render_allocation, render_executive_dashboard, render_executive_value,
    render_negotiation, render_scenario_table, render_should_cost_section,
    render_supplier_snapshot, render_tco_breakdown,
)
from modules.decision_engine import generate_decision, generate_executive_narrative
from modules.executive_outputs import (
    generate_executive_memo, generate_explainability_panel,
    generate_interview_talking_points, generate_supplier_email,
)
from modules.exports import (
    build_decision_package_json, build_excel_workbook,
    dataframe_to_csv_bytes, text_to_bytes,
)
from modules.negotiation import generate_negotiation_playbook, simulate_negotiation
from modules.negotiation_engine import build_negotiation_intelligence
from modules.procurement_intelligence_ui import render_procurement_intelligence
from modules.recommendation import best_value_decision, executive_value_breakdown, recommendation_confidence
from modules.risk_intelligence import assess_procurement_risks
from modules.scenario import run_scenario_table
from modules.scenario_engine import SCENARIOS, run_intelligence_scenario
from modules.scoring import enrich_supplier_scores
from modules.sidebar import render_sidebar
from modules.strategy_engine import recommend_strategy
from modules.validation import validate_rfq_dataframe, validate_scored_output

st.set_page_config(page_title=APP_NAME, page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

assumptions = render_sidebar()
profile = ensure_category_profile(assumptions.get("category_profile"))
assumptions["category_profile"] = profile

st.title(APP_NAME)
st.subheader(EDITION)
st.caption("Transparent, category-aware procurement decision intelligence for RFQ analysis, should-cost, TCO, risk, ESG, allocation, negotiation, and executive recommendations.")
st.success(f"{BUILD} — category-specific packaging and raw-material engines are active.")

with st.expander("Selected Category Intelligence", expanded=True):
    c1, c2, c3 = st.columns(3)
    c1.metric("Category", profile["category"])
    c2.metric("Commodity", profile["selected_commodity"])
    c3.metric("Engine Status", profile["engine_status"])
    st.write(f"**Cost model:** {profile['cost_model']}")
    st.write(f"**Risk model:** {profile['risk_model']}")
    st.write("**Primary cost drivers:** " + ", ".join(profile["primary_cost_drivers"]))
    st.write("**Risk signals:** " + ", ".join(profile["risk_signals"]))
    st.caption(profile["implementation_note"])

uploaded_file = None
if assumptions["data_source"] == "Upload RFQ CSV/Excel":
    uploaded_file = st.file_uploader("Upload RFQ CSV or Excel file", type=["csv", "xlsx"])

try:
    suppliers_df = load_uploaded_rfq(uploaded_file) if uploaded_file is not None else get_demo_data(
        assumptions["category"], assumptions["commodity"]
    )
except Exception as exc:
    st.error(f"The RFQ file could not be read: {exc}")
    st.stop()

validation = validate_rfq_dataframe(suppliers_df)
for warning in validation["warnings"]:
    st.warning(warning)
if not validation["is_valid"]:
    for error in validation["errors"]:
        st.error(error)
    st.stop()

try:
    scored_df = enrich_supplier_scores(suppliers_df, assumptions)
except Exception as exc:
    st.error(f"Supplier scoring failed. Review the uploaded data and assumptions. Technical detail: {exc}")
    st.stop()

output_validation = validate_scored_output(scored_df)
if not output_validation["is_valid"]:
    for error in output_validation["errors"]:
        st.error(error)
    st.stop()

recommended = scored_df.iloc[0]
lowest = scored_df.sort_values("Quoted Unit Price USD").iloc[0]
confidence = recommendation_confidence(scored_df)
should_cost, should_cost_df = calculate_category_should_cost(assumptions)

decision = best_value_decision(scored_df)
value_metrics = executive_value_breakdown(scored_df, assumptions["annual_volume"], should_cost["target_unit_cost_usd"])
allocation_df = recommend_allocation(
    scored_df,
    annual_volume=assumptions["annual_volume"],
    max_supplier_share=assumptions["max_supplier_share"],
    min_backup_share=assumptions["min_backup_share"],
    min_risk_score=assumptions["min_risk_score"],
    min_esg_score=assumptions["min_esg_score"],
)
scenario_df = run_scenario_table(suppliers_df, assumptions)
negotiation_result = simulate_negotiation(recommended, assumptions["annual_volume"])
playbook_text = generate_negotiation_playbook(
    recommended, should_cost["target_unit_cost_usd"], lowest["Supplier"],
    lowest["Quoted Unit Price USD"], negotiation_result["annual_saving_usd"],
)

optimized_allocation = optimize_allocation(scored_df, assumptions["annual_volume"])
risk_result = assess_procurement_risks(scored_df, optimized_allocation["allocation_df"])
strategy_result = recommend_strategy(scored_df, assumptions["annual_volume"])
intelligence_decision = generate_decision(scored_df, optimized_allocation["allocation_df"], risk_result)
negotiation_intelligence = build_negotiation_intelligence(scored_df, assumptions["annual_volume"], should_cost["target_unit_cost_usd"])
selected_scenario = st.sidebar.selectbox("Procurement Intelligence Scenario", list(SCENARIOS.keys()), index=0)
intelligence_scenario_result = run_intelligence_scenario(suppliers_df, assumptions, selected_scenario)
executive_narrative = generate_executive_narrative(
    intelligence_decision, strategy_result, optimized_allocation, risk_result,
    value_metrics["estimated_ebitda_opportunity_usd"],
)

executive_memo = generate_executive_memo(scored_df, allocation_df, value_metrics, confidence)
supplier_email = generate_supplier_email(recommended, should_cost["target_unit_cost_usd"], assumptions["annual_volume"])
explainability_text = generate_explainability_panel(recommended)
interview_talking_points = generate_interview_talking_points()
excel_package = build_excel_workbook(scored_df, should_cost_df, allocation_df, scenario_df)
json_package = build_decision_package_json(recommended, value_metrics, allocation_df, scenario_df, negotiation_result)

render_executive_dashboard(scored_df, assumptions, confidence)
st.markdown("---")

tabs = st.tabs([
    "1. Decision Summary", "2. Cost & Risk", "3. Scenarios & Negotiation",
    "4. Procurement Intelligence", "5. Executive Outputs", "6. Downloads", "7. Interview Guide",
])

with tabs[0]:
    st.header("Lowest Price vs Best Value Decision")
    st.write(decision["message"])
    render_executive_value(value_metrics, assumptions)
    render_supplier_snapshot(scored_df)

with tabs[1]:
    st.subheader(f"{assumptions['category']} — {assumptions['commodity']}")
    render_should_cost_section(should_cost_df, should_cost["target_unit_cost_usd"], assumptions)
    render_tco_breakdown(scored_df, assumptions)
    with st.expander("Visible Category Risk Assumptions"):
        if assumptions["category"] == "Raw Material Procurement":
            st.write("Risk includes commodity volatility, import dependency, supplier concentration, substitution, FX, capacity, logistics, quality, and commercial exposure.")
        else:
            st.write("Risk includes payment terms, incoterms, lead time, MOQ, OTIF, quality, and packaging continuity exposure.")

with tabs[2]:
    render_allocation(allocation_df, assumptions)
    render_scenario_table(scenario_df, assumptions)
    render_negotiation(playbook_text, negotiation_result)

with tabs[3]:
    render_procurement_intelligence(
        intelligence_decision, strategy_result, optimized_allocation,
        negotiation_intelligence, risk_result, intelligence_scenario_result,
        executive_narrative,
    )

with tabs[4]:
    st.header("Executive Sourcing Memo")
    st.text_area("Generated executive sourcing memo", executive_memo, height=520)
    st.header("Supplier Clarification Email")
    st.text_area("Generated supplier clarification email", supplier_email, height=460)
    st.header("AI-Style Explainability Panel")
    st.write(explainability_text)
    st.caption("Transparent, rule-guided, auditable, procurement-controlled, and not a black-box award decision.")

with tabs[5]:
    st.header("Download Decision Package")
    c1, c2, c3 = st.columns(3)
    c1.download_button("Download Excel Analysis", excel_package, "ai_procurement_copilot_analysis.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    c2.download_button("Download Executive Memo", text_to_bytes(executive_memo), "executive_sourcing_memo.txt", "text/plain")
    c3.download_button("Download Supplier Email", text_to_bytes(supplier_email), "supplier_clarification_email.txt", "text/plain")
    c4, c5, c6 = st.columns(3)
    c4.download_button("Download Supplier Scores CSV", dataframe_to_csv_bytes(scored_df), "supplier_scores.csv", "text/csv")
    c5.download_button("Download Allocation CSV", dataframe_to_csv_bytes(allocation_df), "supplier_allocation.csv", "text/csv")
    c6.download_button("Download Decision JSON", json_package, "procurement_decision_package.json", "application/json")

with tabs[6]:
    st.header("Interview Talking Points")
    st.write(interview_talking_points)
    st.info("Positioning: a category-aware procurement decision-support product with transparent, auditable human governance.")

st.markdown("---")
st.caption(f"{BUILD} | Application status: {STATUS}")
