# =====================================================
# AI PROCUREMENT COPILOT
# Portfolio Edition v1.0
# Build 0.5 — Executive Communication Layer
# =====================================================

import streamlit as st

from modules.allocation import recommend_allocation
from modules.config import APP_NAME, EDITION, STATUS
from modules.data_loader import get_demo_suppliers, load_uploaded_rfq
from modules.dashboard import (
    render_allocation,
    render_executive_dashboard,
    render_executive_value,
    render_negotiation,
    render_scenario_table,
    render_should_cost_section,
    render_supplier_snapshot,
    render_tco_breakdown,
)
from modules.executive_outputs import (
    generate_executive_memo,
    generate_explainability_panel,
    generate_interview_talking_points,
    generate_supplier_email,
)
from modules.negotiation import generate_negotiation_playbook, simulate_negotiation
from modules.recommendation import best_value_decision, executive_value_breakdown, recommendation_confidence
from modules.rfq import validate_rfq_columns
from modules.scenario import run_scenario_table
from modules.scoring import enrich_supplier_scores
from modules.should_cost import calculate_packaging_should_cost, should_cost_dataframe
from modules.sidebar import render_sidebar


st.set_page_config(
    page_title=APP_NAME,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


assumptions = render_sidebar()

st.title(APP_NAME)
st.subheader(EDITION)

st.info(
    "Build 0.5 adds the executive communication layer: executive sourcing memo, supplier clarification email, "
    "AI-style explainability, and interview talking points."
)

st.markdown("---")

uploaded_file = None
if assumptions["data_source"] == "Upload RFQ CSV/Excel":
    uploaded_file = st.file_uploader("Upload RFQ CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    suppliers_df = load_uploaded_rfq(uploaded_file)
    missing_columns = validate_rfq_columns(suppliers_df)
    if missing_columns:
        st.warning(f"Uploaded file is missing expected columns: {', '.join(missing_columns)}")
else:
    suppliers_df = get_demo_suppliers()

scored_df = enrich_supplier_scores(suppliers_df, assumptions)
recommended = scored_df.iloc[0]
lowest = scored_df.sort_values("Quoted Unit Price USD").iloc[0]
confidence = recommendation_confidence(scored_df)

should_cost = calculate_packaging_should_cost(
    raw_material_shock=assumptions["raw_material_shock"],
    freight_shock=assumptions["freight_shock"],
)
should_cost_df = should_cost_dataframe(
    should_cost,
    annual_volume=assumptions["annual_volume"] * (1 + assumptions["demand_change"]),
    fx_rate=assumptions["fx_rate"],
)

decision = best_value_decision(scored_df)
value_metrics = executive_value_breakdown(
    scored_df,
    assumptions["annual_volume"],
    should_cost["target_unit_cost_usd"],
)
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
    recommended,
    should_cost["target_unit_cost_usd"],
    lowest["Supplier"],
    lowest["Quoted Unit Price USD"],
    negotiation_result["annual_saving_usd"],
)

executive_memo = generate_executive_memo(scored_df, allocation_df, value_metrics, confidence)
supplier_email = generate_supplier_email(
    recommended,
    should_cost["target_unit_cost_usd"],
    assumptions["annual_volume"],
)
explainability_text = generate_explainability_panel(recommended)
interview_talking_points = generate_interview_talking_points()

render_executive_dashboard(scored_df, assumptions, confidence)
st.markdown("---")

st.header("Lowest Price vs Best Value Decision")
st.write(decision["message"])

st.markdown("---")
render_executive_value(value_metrics, assumptions)
st.markdown("---")
render_supplier_snapshot(scored_df)
st.markdown("---")
render_should_cost_section(should_cost_df, should_cost["target_unit_cost_usd"], assumptions)
st.markdown("---")
render_tco_breakdown(scored_df, assumptions)
st.markdown("---")
render_allocation(allocation_df, assumptions)
st.markdown("---")
render_scenario_table(scenario_df, assumptions)
st.markdown("---")
render_negotiation(playbook_text, negotiation_result)

st.markdown("---")
st.header("Executive Sourcing Memo")
st.text_area("Generated executive sourcing memo", executive_memo, height=520)

st.markdown("---")
st.header("Supplier Clarification Email")
st.text_area("Generated supplier clarification email", supplier_email, height=460)

st.markdown("---")
st.header("AI-Style Explainability Panel")
st.write(explainability_text)
st.caption(
    "This recommendation is transparent, rule-guided, auditable, and procurement-controlled. It is not a black-box AI award decision."
)

st.markdown("---")
st.header("Interview Talking Points")
st.write(interview_talking_points)

st.markdown("---")
st.header("Risk Assumptions")
st.write(
    "Risk scoring is rule-guided and auditable. Current factors include payment terms, incoterms, lead time, MOQ, OTIF, and quality PPM."
)

st.header("Build Status")
st.write("**Current Build:** Build 0.5 — Executive Communication Layer")
st.write(f"**Status:** {STATUS}")
st.write("**Next Build:** Build 0.6 — UX Refinement, Testing, Documentation, and Portfolio Polish")
