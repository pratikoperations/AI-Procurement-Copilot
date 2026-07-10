# =====================================================
# AI PROCUREMENT COPILOT
# Portfolio Edition v1.0
# Build 0.7 — Release Candidate Preparation
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
from modules.exports import (
    build_decision_package_json,
    build_excel_workbook,
    dataframe_to_csv_bytes,
    text_to_bytes,
)
from modules.negotiation import generate_negotiation_playbook, simulate_negotiation
from modules.recommendation import best_value_decision, executive_value_breakdown, recommendation_confidence
from modules.scenario import run_scenario_table
from modules.scoring import enrich_supplier_scores
from modules.should_cost import calculate_packaging_should_cost, should_cost_dataframe
from modules.sidebar import render_sidebar
from modules.validation import validate_rfq_dataframe, validate_scored_output


st.set_page_config(
    page_title=APP_NAME,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

assumptions = render_sidebar()

st.title(APP_NAME)
st.subheader(EDITION)
st.caption(
    "Transparent, rule-guided procurement decision intelligence for RFQ analysis, packaging should-cost, TCO, risk, ESG, allocation, negotiation, and executive recommendations."
)

st.success(
    "Build 0.7 release-candidate preparation adds downloadable decision packages and a polished six-step interview workflow."
)

uploaded_file = None
if assumptions["data_source"] == "Upload RFQ CSV/Excel":
    uploaded_file = st.file_uploader(
        "Upload RFQ CSV or Excel file",
        type=["csv", "xlsx"],
        help="Use the sample schema in sample_data/sample_packaging_rfq.csv.",
    )

if uploaded_file is not None:
    try:
        suppliers_df = load_uploaded_rfq(uploaded_file)
    except Exception as exc:
        st.error(f"The RFQ file could not be read: {exc}")
        st.stop()
else:
    suppliers_df = get_demo_suppliers()

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

should_cost = calculate_packaging_should_cost(
    raw_material_shock=assumptions["raw_material_shock"],
    freight_shock=assumptions["freight_shock"],
)
effective_volume = assumptions["annual_volume"] * (1 + assumptions["demand_change"])
should_cost_df = should_cost_dataframe(
    should_cost,
    annual_volume=effective_volume,
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

excel_package = build_excel_workbook(scored_df, should_cost_df, allocation_df, scenario_df)
json_package = build_decision_package_json(
    recommended,
    value_metrics,
    allocation_df,
    scenario_df,
    negotiation_result,
)

render_executive_dashboard(scored_df, assumptions, confidence)
st.markdown("---")

summary_tab, analysis_tab, strategy_tab, executive_tab, downloads_tab, interview_tab = st.tabs(
    [
        "1. Decision Summary",
        "2. Cost & Risk",
        "3. Scenarios & Negotiation",
        "4. Executive Outputs",
        "5. Downloads",
        "6. Interview Guide",
    ]
)

with summary_tab:
    st.header("Lowest Price vs Best Value Decision")
    st.write(decision["message"])
    render_executive_value(value_metrics, assumptions)
    render_supplier_snapshot(scored_df)

with analysis_tab:
    render_should_cost_section(should_cost_df, should_cost["target_unit_cost_usd"], assumptions)
    render_tco_breakdown(scored_df, assumptions)

    with st.expander("Visible Risk Assumptions"):
        st.write(
            "Risk scoring is rule-guided and auditable. Current factors include payment terms, incoterms, lead time, MOQ, OTIF, and quality PPM."
        )
        st.write(
            "The risk-adjusted TCO model converts structured supplier risk into an expected monetary value penalty rather than hiding risk inside an unexplained total score."
        )

with strategy_tab:
    render_allocation(allocation_df, assumptions)
    render_scenario_table(scenario_df, assumptions)
    render_negotiation(playbook_text, negotiation_result)

with executive_tab:
    st.header("Executive Sourcing Memo")
    st.text_area("Generated executive sourcing memo", executive_memo, height=520)

    st.header("Supplier Clarification Email")
    st.text_area("Generated supplier clarification email", supplier_email, height=460)

    st.header("AI-Style Explainability Panel")
    st.write(explainability_text)
    st.caption(
        "This recommendation is transparent, rule-guided, auditable, and procurement-controlled. It is not a black-box AI award decision."
    )

with downloads_tab:
    st.header("Download Decision Package")
    st.write("Export the analysis for interview demonstration, review, or handoff.")

    c1, c2, c3 = st.columns(3)
    c1.download_button(
        "Download Excel Analysis",
        data=excel_package,
        file_name="ai_procurement_copilot_analysis.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    c2.download_button(
        "Download Executive Memo",
        data=text_to_bytes(executive_memo),
        file_name="executive_sourcing_memo.txt",
        mime="text/plain",
    )
    c3.download_button(
        "Download Supplier Email",
        data=text_to_bytes(supplier_email),
        file_name="supplier_clarification_email.txt",
        mime="text/plain",
    )

    c4, c5, c6 = st.columns(3)
    c4.download_button(
        "Download Supplier Scores CSV",
        data=dataframe_to_csv_bytes(scored_df),
        file_name="supplier_scores.csv",
        mime="text/csv",
    )
    c5.download_button(
        "Download Allocation CSV",
        data=dataframe_to_csv_bytes(allocation_df),
        file_name="supplier_allocation.csv",
        mime="text/csv",
    )
    c6.download_button(
        "Download Decision JSON",
        data=json_package,
        file_name="procurement_decision_package.json",
        mime="application/json",
    )

with interview_tab:
    st.header("Interview Talking Points")
    st.write(interview_talking_points)

    st.subheader("Recommended 7-Minute Demo Flow")
    st.write(
        "1. Explain the business problem. 2. Load the RFQ. 3. Show best value vs lowest price. "
        "4. Explain should-cost and risk-adjusted TCO. 5. Show allocation and scenario resilience. "
        "6. Demonstrate negotiation and executive outputs. 7. Close with explainability and business impact."
    )

    st.info(
        "Interview positioning: this is a procurement decision-support product, not an autonomous award engine. Human judgment, governance, and auditability remain central."
    )

st.markdown("---")
st.caption(
    "Build 0.7 — Defect Remediation, Visual Polish, Downloadable Outputs, and Release-Candidate Preparation | "
    f"Application status: {STATUS}"
)
