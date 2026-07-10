# =====================================================
# AI PROCUREMENT COPILOT
# Portfolio Edition v1.0
# Build 0.3 — Packaging Procurement Engines
# =====================================================

import streamlit as st

from modules.config import APP_NAME, EDITION, STATUS
from modules.data_loader import get_demo_suppliers, load_uploaded_rfq
from modules.dashboard import (
    render_executive_dashboard,
    render_should_cost_section,
    render_supplier_snapshot,
    render_tco_breakdown,
)
from modules.rfq import validate_rfq_columns
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
    "Build 0.3 adds working packaging procurement engines: should-cost, advanced TCO, structured risk, ESG, performance, and weighted supplier scoring."
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

should_cost = calculate_packaging_should_cost(
    raw_material_shock=assumptions["raw_material_shock"],
    freight_shock=assumptions["freight_shock"],
)
should_cost_df = should_cost_dataframe(
    should_cost,
    annual_volume=assumptions["annual_volume"] * (1 + assumptions["demand_change"]),
    fx_rate=assumptions["fx_rate"],
)

render_executive_dashboard(scored_df, assumptions)
st.markdown("---")
render_supplier_snapshot(scored_df)
st.markdown("---")
render_should_cost_section(should_cost_df, should_cost["target_unit_cost_usd"], assumptions)
st.markdown("---")
render_tco_breakdown(scored_df, assumptions)

st.markdown("---")
st.header("Risk Assumptions")
st.write(
    "Risk scoring is rule-guided and auditable. Current factors include payment terms, incoterms, lead time, MOQ, OTIF, and quality PPM."
)

st.header("Build Status")
st.write("**Current Build:** Build 0.3 — Packaging Procurement Engines")
st.write(f"**Status:** {STATUS}")
st.write("**Next Build:** Build 0.4 — Decision Intelligence, Allocation, Scenario Simulation, and Negotiation")
