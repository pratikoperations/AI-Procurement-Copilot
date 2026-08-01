"""AI Procurement Copilot — Portfolio Presentation Release v1.2."""

import json
import streamlit as st

from modules.allocation import recommend_allocation
from modules.allocation_optimizer import optimize_allocation
from modules.category_cost_router import calculate_category_should_cost
from modules.category_engine import ensure_category_profile
from modules.config import APP_NAME, BUILD, EDITION, STATUS
from modules.currency_unit_governance import normalize_comparison_basis, validate_category_unit
from modules.data_loader import get_demo_data, load_uploaded_rfq
from modules.dashboard import (
    render_allocation, render_executive_dashboard, render_executive_value,
    render_negotiation, render_scenario_table, render_should_cost_section,
    render_supplier_snapshot, render_tco_breakdown,
)
from modules.decision_engine import generate_decision, generate_executive_narrative
from modules.executive_outputs import (
    generate_executive_memo, generate_explainability_panel, generate_supplier_email,
)
from modules.exports import (
    build_c2_export_manifest, build_decision_package_json, build_excel_workbook,
    build_readable_allocation, build_readable_supplier_comparison,
    build_readable_supplier_scores, dataframe_to_csv_bytes, text_to_bytes,
)
from modules.negotiation import generate_negotiation_playbook, govern_negotiation_brief, simulate_negotiation
from modules.negotiation_engine import build_negotiation_intelligence
from modules.procurement_intelligence_ui import render_procurement_intelligence
from modules.ranking_input_models import RankingMappingConfirmation
from modules.recommendation import best_value_decision, executive_value_breakdown, recommendation_confidence
from modules.rfq_analytical_handoff import filter_analytical_assumptions, run_engine_stages
from modules.rfq_integration_controller import run_governed_review
from modules.rfq_review_state import ReviewState
from modules.rfq_review_ui import (
    render_event_selection, render_governed_review, render_handoff_confirmation,
    render_item_selection, render_mapping_reviews, render_ranking_mapping_confirmations,
    render_warning_acknowledgements,
)
from modules.risk_intelligence import assess_procurement_risks
from modules.scenario import run_scenario_table
from modules.scenario_engine import run_intelligence_scenario
from modules.scoring import enrich_supplier_scores
from modules.sidebar import render_sidebar
from modules.strategy_engine import recommend_strategy
from modules.supplier_comparison import build_supplier_intelligence
from modules.supplier_intelligence_currency_ui import render_supplier_intelligence
from modules.validation import validate_rfq_dataframe, validate_scored_output
from modules.validation_assurance import run_validation_assurance, safe_executive_text

st.set_page_config(page_title=APP_NAME, page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

assumptions = render_sidebar()
profile = ensure_category_profile(assumptions.get("category_profile"))
assumptions["category_profile"] = profile
assumptions.setdefault("annual_volume_unit", profile.get("unit", "unit"))
selected_laminate_structure = (
    assumptions.get("laminate_structure")
    if assumptions.get("category") == "Packaging Procurement"
    and assumptions.get("commodity") == "Flexible Laminates"
    else None
)

st.title(f"{APP_NAME} v1.2")
st.subheader("Governed, category-aware procurement decision support for RFQ comparison and sourcing evaluation.")
st.caption(
    "Built for procurement managers, category managers and sourcing teams reviewing supplier quotations, "
    "commercial trade-offs and award readiness."
)
status_columns = st.columns(4)
status_columns[0].info("Portfolio demonstration")
status_columns[1].info("Read-only operation")
status_columns[2].info("Validation-gated")
status_columns[3].info("No live ERP integration")
st.warning(
    "This application supports human procurement review. It does not claim production deployment, "
    "autonomous awards, live ERP integration or realized savings."
)
st.caption(f"{EDITION} | {BUILD}")

with st.expander("Selected Category Intelligence", expanded=False):
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
is_governed_route = assumptions["data_source"] == "Governed v1.3 Workbook Review Preview"
if assumptions["data_source"] == "Upload RFQ CSV/Excel":
    uploaded_file = st.file_uploader("Upload RFQ CSV or Excel file", type=["csv", "xlsx"])
elif is_governed_route:
    uploaded_file = st.file_uploader("Upload governed v1.3 workbook", type=["xlsx"])

if is_governed_route:
    confirmed_mappings = tuple(st.session_state.get("governed_v13_confirmed_mappings", ()))
    ranking_confirmations = tuple(
        RankingMappingConfirmation(**item)
        for item in st.session_state.get("governed_v13_ranking_confirmations", ())
    )
    selected_event = st.session_state.get("governed_v13_selected_event")
    selected_number = st.session_state.get("governed_v13_selected_rfq_number")
    selected_item = st.session_state.get("governed_v13_selected_rfq_item")
    acknowledged = tuple(st.session_state.get("governed_v13_acknowledged_warnings", ()))
    handoff_digest = st.session_state.get("governed_v13_handoff_digest")

    governed_result = run_governed_review(
        uploaded_file,
        filename=None if uploaded_file is None else uploaded_file.name,
        selected_sourcing_event_id=selected_event,
        selected_rfq_number=selected_number,
        selected_rfq_item=selected_item,
        confirmed_mappings=confirmed_mappings,
        ranking_confirmations=ranking_confirmations,
        acknowledged_warning_codes=acknowledged,
        comparison_currency="USD",
        display_currency_mode=assumptions["display_currency"],
        handoff_confirmation_digest=handoff_digest,
        analytical_assumptions=filter_analytical_assumptions(assumptions),
    )

    if governed_result.review_state is ReviewState.MAPPING_CONFIRMATION_REQUIRED and governed_result.adapter_result is not None:
        render_governed_review(governed_result)
        selected_mappings = render_mapping_reviews(governed_result.adapter_result)
        selected_ranking = render_ranking_mapping_confirmations(governed_result.adapter_result)
        pending_quotes = sum(1 for item in governed_result.adapter_result.mapping_reviews if item.requires_confirmation and item.sheet != "SUPPLIER_RANKING_INPUTS")
        pending_ranking = [item for item in governed_result.adapter_result.mapping_reviews if item.requires_confirmation and item.sheet == "SUPPLIER_RANKING_INPUTS" and item.canonical_field]
        required_contexts = sum(len({
            str(record.value_origins.get(item.canonical_field) or "")
            for record in governed_result.adapter_result.supplier_ranking_inputs
            if record.canonical_values.get(item.canonical_field) is not None and record.value_origins.get(item.canonical_field)
        }) for item in pending_ranking)
        if len(selected_mappings) == pending_quotes and len(selected_ranking) == required_contexts and st.button("Apply mapping confirmations"):
            st.session_state["governed_v13_confirmed_mappings"] = selected_mappings
            st.session_state["governed_v13_ranking_confirmations"] = tuple(item.__dict__ for item in selected_ranking)
            for key in (
                "governed_v13_selected_event", "governed_v13_selected_rfq_number",
                "governed_v13_selected_rfq_item", "governed_v13_acknowledged_warnings",
                "governed_v13_handoff_digest", "governed_v13_handoff_manifest_digest",
                "governed_v13_handoff_confirmed_at", "governed_v13_handoff_contract_version",
            ):
                st.session_state.pop(key, None)
            st.rerun()
        st.stop()

    if governed_result.review_state is ReviewState.EVENT_SELECTION_REQUIRED and governed_result.adapter_result is not None:
        render_governed_review(governed_result)
        event = render_event_selection(governed_result.adapter_result)
        if event and st.button("Apply sourcing-event selection"):
            st.session_state["governed_v13_selected_event"] = event
            for key in ("governed_v13_selected_rfq_number", "governed_v13_selected_rfq_item", "governed_v13_acknowledged_warnings", "governed_v13_handoff_digest"):
                st.session_state.pop(key, None)
            st.rerun()
        st.stop()

    if governed_result.review_state is ReviewState.ITEM_SELECTION_REQUIRED and governed_result.orchestration_result is not None:
        render_governed_review(governed_result)
        rfq_number, rfq_item = render_item_selection(governed_result.orchestration_result)
        if rfq_number and rfq_item and st.button("Apply RFQ-item selection"):
            st.session_state["governed_v13_selected_rfq_number"] = rfq_number
            st.session_state["governed_v13_selected_rfq_item"] = rfq_item
            st.session_state.pop("governed_v13_acknowledged_warnings", None)
            st.session_state.pop("governed_v13_handoff_digest", None)
            st.rerun()
        st.stop()

    if governed_result.review_state is ReviewState.CONDITIONAL_REVIEW_REQUIRED and governed_result.orchestration_result is not None and governed_result.adapter_result is not None:
        render_governed_review(governed_result)
        warning_codes = render_warning_acknowledgements(governed_result.orchestration_result, governed_result.adapter_result.mode)
        if warning_codes and st.button("Apply warning acknowledgements"):
            st.session_state["governed_v13_acknowledged_warnings"] = warning_codes
            st.session_state.pop("governed_v13_handoff_digest", None)
            st.rerun()
        st.stop()

    render_governed_review(governed_result)
    if render_handoff_confirmation(governed_result):
        st.session_state["governed_v13_handoff_digest"] = governed_result.handoff_digest
        st.session_state["governed_v13_handoff_manifest_digest"] = governed_result.handoff_digest
        st.session_state["governed_v13_handoff_contract_version"] = "AIPC-E2-HANDOFF-1.3.1"
        st.rerun()
    if governed_result.dataframe is None or not governed_result.analysis_handoff_allowed:
        st.stop()
    suppliers_df = governed_result.dataframe
else:
    try:
        suppliers_df = load_uploaded_rfq(uploaded_file) if uploaded_file is not None else get_demo_data(
            assumptions["category"],
            assumptions["commodity"],
            selected_structure=selected_laminate_structure,
        )
        suppliers_df = normalize_comparison_basis(suppliers_df, assumptions.get("fx_rate"), "USD")
    except Exception as exc:
        st.error(f"The RFQ file could not be read or normalized: {exc}")
        st.stop()

for warning in validate_category_unit(suppliers_df, assumptions["category"], assumptions["commodity"]):
    st.error(warning)
    st.stop()

currency_governance = suppliers_df.attrs.get("currency_unit_governance", {})
for issue in currency_governance.get("blockers", []):
    st.error(issue)
if currency_governance.get("blockers"):
    st.stop()

if is_governed_route:
    handoff_digest = str(suppliers_df.attrs.get("handoff_manifest_digest") or "")

    def _input_validation(_outputs):
        result = validate_rfq_dataframe(
            suppliers_df,
            category=assumptions["category"],
            commodity=assumptions["commodity"],
            selected_structure=selected_laminate_structure,
        )
        if not result["is_valid"]:
            raise ValueError("; ".join(result["errors"]))
        return result

    def _scoring(_outputs):
        return enrich_supplier_scores(suppliers_df, assumptions)

    def _scored_validation(outputs):
        result = validate_scored_output(outputs["SCORING_TCO"])
        if not result["is_valid"]:
            raise ValueError("; ".join(result["errors"]))
        return result

    def _recommendation(outputs):
        scored = outputs["SCORING_TCO"]
        recommended_row = scored.iloc[0]
        lowest_row = scored.sort_values("Quoted Unit Price USD").iloc[0]
        confidence_value = recommendation_confidence(scored)
        should_cost_value, should_cost_table = calculate_category_should_cost(assumptions)
        decision_value = best_value_decision(scored)
        value = executive_value_breakdown(scored, assumptions["annual_volume"], should_cost_value["target_unit_cost_usd"])
        return {"recommended": recommended_row, "lowest": lowest_row, "confidence": confidence_value, "should_cost": should_cost_value, "should_cost_df": should_cost_table, "decision": decision_value, "value_metrics": value}

    def _allocation(outputs):
        scored = outputs["SCORING_TCO"]
        allocation = recommend_allocation(
            scored,
            annual_volume=assumptions["annual_volume"],
            max_supplier_share=assumptions["max_supplier_share"],
            min_backup_share=assumptions["min_backup_share"],
            min_risk_score=assumptions["min_risk_score"],
            min_esg_score=assumptions["min_esg_score"],
        )
        optimized = optimize_allocation(scored, assumptions["annual_volume"])
        return {"allocation_df": allocation, "optimized_allocation": optimized}

    def _negotiation(outputs):
        recommendation = outputs["RECOMMENDATION"]
        recommended_row = recommendation["recommended"]
        negotiation = simulate_negotiation(recommended_row, assumptions["annual_volume"])
        playbook = generate_negotiation_playbook(
            recommended_row, recommendation["should_cost"]["target_unit_cost_usd"],
            recommendation["lowest"]["Supplier"], recommendation["lowest"]["Quoted Unit Price USD"],
            negotiation["annual_saving_usd"],
        )
        return {"scenario_df": run_scenario_table(suppliers_df, assumptions), "negotiation_result": negotiation, "playbook_text": playbook}

    execution = run_engine_stages(suppliers_df, handoff_digest, {
        "INPUT_VALIDATION": _input_validation,
        "SCORING_TCO": _scoring,
        "SCORED_OUTPUT_VALIDATION": _scored_validation,
        "RECOMMENDATION": _recommendation,
        "ALLOCATION": _allocation,
        "NEGOTIATION": _negotiation,
    })
    with st.expander("Governed engine-stage audit", expanded=False):
        st.dataframe([item.__dict__ for item in execution.stages], use_container_width=True)
    if not execution.completed:
        failed = next(item for item in execution.stages if item.status == "BLOCKED")
        st.error(f"Governed analytical execution stopped at {failed.stage}: {failed.message}")
        st.stop()
    validation = execution.outputs["INPUT_VALIDATION"]
    scored_df = execution.outputs["SCORING_TCO"]
    recommendation_bundle = execution.outputs["RECOMMENDATION"]
    recommended = recommendation_bundle["recommended"]
    lowest = recommendation_bundle["lowest"]
    confidence = recommendation_bundle["confidence"]
    should_cost = recommendation_bundle["should_cost"]
    should_cost_df = recommendation_bundle["should_cost_df"]
    decision = recommendation_bundle["decision"]
    value_metrics = recommendation_bundle["value_metrics"]
    allocation_bundle = execution.outputs["ALLOCATION"]
    allocation_df = allocation_bundle["allocation_df"]
    optimized_allocation = allocation_bundle["optimized_allocation"]
    negotiation_bundle = execution.outputs["NEGOTIATION"]
    scenario_df = negotiation_bundle["scenario_df"]
    negotiation_result = negotiation_bundle["negotiation_result"]
    playbook_text = negotiation_bundle["playbook_text"]
else:
    validation = validate_rfq_dataframe(
        suppliers_df,
        category=assumptions["category"],
        commodity=assumptions["commodity"],
        selected_structure=selected_laminate_structure,
    )
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
selected_scenario = assumptions["procurement_intelligence_scenario"]
intelligence_scenario_result = run_intelligence_scenario(suppliers_df, assumptions, selected_scenario)
provisional_executive_narrative = generate_executive_narrative(
    intelligence_decision, strategy_result, optimized_allocation, risk_result,
    value_metrics["estimated_ebitda_opportunity_usd"],
)

supplier_intelligence = build_supplier_intelligence(scored_df, assumptions["category"], assumptions["commodity"])
assurance = run_validation_assurance(
    suppliers_df, scored_df, optimized_allocation["allocation_df"],
    supplier_intelligence["profiles"], assumptions, validation,
)
data_confidence = assurance["data_confidence"]
business_rules = assurance["business_rules"]
eligibility = assurance["eligibility"]
playbook_text = govern_negotiation_brief(playbook_text, eligibility)

raw_executive_memo = generate_executive_memo(
    scored_df, allocation_df, value_metrics, confidence, eligibility, data_confidence
)
executive_memo = safe_executive_text(eligibility, raw_executive_memo, raw_executive_memo)
executive_narrative = safe_executive_text(eligibility, provisional_executive_narrative, provisional_executive_narrative)
supplier_narrative = safe_executive_text(
    eligibility, supplier_intelligence["executive_narrative"], supplier_intelligence["executive_narrative"]
)
supplier_intelligence["executive_narrative"] = supplier_narrative
unit = assumptions["annual_volume_unit"]
supplier_email = generate_supplier_email(
    recommended,
    should_cost["target_unit_cost_usd"],
    assumptions["annual_volume"],
    assumptions["category"],
    assumptions["commodity"],
    unit,
    eligibility,
)
explainability_text = generate_explainability_panel(recommended)
display_currency = assumptions["display_currency"]
fx_rate = assumptions["fx_rate"]
volume = assumptions["annual_volume"]
volume_unit = assumptions["annual_volume_unit"]
readable_scores = build_readable_supplier_scores(
    scored_df, data_confidence, eligibility,
    display_currency=display_currency, fx_rate=fx_rate,
    annual_volume=volume, annual_volume_unit=volume_unit,
)
readable_comparison = build_readable_supplier_comparison(
    supplier_intelligence["comparison_df"], data_confidence, eligibility,
    display_currency=display_currency, fx_rate=fx_rate,
    annual_volume=volume, annual_volume_unit=volume_unit,
)
readable_allocation = build_readable_allocation(
    allocation_df, display_currency, fx_rate,
    annual_volume=volume, annual_volume_unit=volume_unit,
)
is_flexible_laminates = (
    assumptions.get("category") == "Packaging Procurement"
    and assumptions.get("commodity") == "Flexible Laminates"
)
c2_manifest = (
    build_c2_export_manifest(
        scored_df,
        allocation_df,
        optimized_allocation["allocation_df"],
        scenario_df,
    )
    if is_flexible_laminates
    else None
)
excel_package = build_excel_workbook(
    scored_df, should_cost_df, allocation_df, scenario_df,
    readable_scores, readable_comparison,
    display_currency=display_currency, fx_rate=fx_rate,
    annual_volume=volume, annual_volume_unit=volume_unit,
    optimized_allocation_df=optimized_allocation["allocation_df"],
    c2_manifest=c2_manifest,
)
json_package = build_decision_package_json(
    recommended, value_metrics, allocation_df, scenario_df,
    negotiation_result, eligibility, c2_manifest=c2_manifest,
)
supplier_profiles_json = json.dumps(supplier_intelligence["profiles"], indent=2, default=str).encode("utf-8")

with st.expander("Validation Assurance Gate", expanded=True):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Eligibility", eligibility["status"])
    c2.metric("Data Confidence", f"{data_confidence['data_confidence_score']}/100")
    c3.metric("Confidence Category", data_confidence["confidence_category"])
    c4.metric("Business Rules", business_rules["status"])
    st.caption(data_confidence["source_label"])
    st.write(data_confidence["explanation"])
    st.write(
        f"**Supplied data:** {data_confidence['actual_supplied_data_percentage']}% | "
        f"**Defaulted:** {data_confidence['defaulted_data_percentage']}% | "
        f"**Missing critical:** {data_confidence['missing_critical_data_percentage']}% | "
        f"**Inferred:** {data_confidence['inferred_data_percentage']}%"
    )
    if business_rules["blocking_issues"]:
        for issue in business_rules["blocking_issues"]:
            st.error(issue)
    if business_rules["non_blocking_issues"]:
        for issue in business_rules["non_blocking_issues"]:
            st.warning(issue)
    if eligibility["status"] in {"Blocked", "Insufficient Data"}:
        st.error(eligibility["reason"])
    elif eligibility["status"] == "Human Review Required":
        st.warning("PROVISIONAL RECOMMENDATION — HUMAN REVIEW REQUIRED")
    elif eligibility["status"] == "Eligible With Conditions":
        st.warning("Recommendation is eligible only with the listed conditions.")
    else:
        st.success("Eligibility checks passed; human approval remains mandatory.")
    for action in eligibility["required_remediation"]:
        st.write(f"- {action}")

render_executive_dashboard(scored_df, assumptions, confidence)
st.markdown("---")

sections = [
    "1. Decision Summary",
    "2. Cost and Risk",
    "3. Scenarios and Negotiation",
    "4. Procurement Intelligence",
    "5. Supplier Intelligence",
    "6. Executive Outputs",
    "7. Downloads",
]
selected_section = st.selectbox(
    "Explore the sourcing workflow",
    sections,
    index=0,
    help="Choose one section at a time. This compact navigation is designed for desktop and mobile use.",
)

if selected_section == sections[0]:
    st.header("Lowest Price vs Best Value Decision")
    if eligibility["final_award_language_allowed"]:
        st.write(decision["message"])
        render_executive_value(value_metrics, assumptions)
    else:
        st.error(f"Final award recommendation withheld: {eligibility['reason']}")
        for issue in eligibility["failed_checks"]:
            st.write(f"- {issue}")
    render_supplier_snapshot(scored_df, assumptions)

elif selected_section == sections[1]:
    st.subheader(f"{assumptions['category']} — {assumptions['commodity']}")
    render_should_cost_section(should_cost_df, should_cost["target_unit_cost_usd"], assumptions)
    render_tco_breakdown(scored_df, assumptions)
    with st.expander("Visible Category Risk Assumptions"):
        if assumptions["category"] == "Raw Material Procurement":
            st.write("Risk includes commodity volatility, import dependency, supplier concentration, substitution, FX, capacity, logistics, quality, and commercial exposure.")
        else:
            st.write("Risk includes payment terms, incoterms, lead time, MOQ, OTIF, quality, and packaging continuity exposure.")

elif selected_section == sections[2]:
    render_allocation(allocation_df, assumptions)
    render_scenario_table(scenario_df, assumptions)
    render_negotiation(playbook_text, negotiation_result, assumptions)

elif selected_section == sections[3]:
    if eligibility["recommendation_allowed"]:
        render_procurement_intelligence(
            intelligence_decision, strategy_result, optimized_allocation,
            negotiation_intelligence, risk_result, intelligence_scenario_result,
            executive_narrative,
        )
    else:
        st.error("Procurement award recommendation is blocked until validation issues are corrected.")
        st.text_area("Validation outcome", executive_narrative, height=380)

elif selected_section == sections[4]:
    if eligibility["status"] != "Eligible":
        st.warning(f"Supplier Intelligence is analytical and provisional. Eligibility status: {eligibility['status']}.")
    render_supplier_intelligence(
        supplier_intelligence,
        display_currency=display_currency,
        fx_rate=fx_rate,
    )

elif selected_section == sections[5]:
    st.header("Executive Sourcing Memo")
    st.text_area("Generated executive sourcing memo", executive_memo, height=520)
    st.header("Supplier Clarification Email")
    st.text_area("Generated supplier clarification email", supplier_email, height=460)
    st.header("AI-Style Explainability Panel")
    st.write(explainability_text)
    st.caption("Transparent, rule-guided, auditable, procurement-controlled, and not a black-box award decision.")

else:
    st.header("Download Decision Package")
    st.subheader("Business-facing outputs")
    c1, c2 = st.columns(2)
    c1.download_button("Download Excel Analysis", excel_package, "ai_procurement_copilot_analysis.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    c2.download_button("Download Executive Memo", text_to_bytes(executive_memo), "executive_sourcing_memo.txt", "text/plain", use_container_width=True)
    c3, c4 = st.columns(2)
    c3.download_button("Download Supplier Email", text_to_bytes(supplier_email), "supplier_clarification_email.txt", "text/plain", use_container_width=True)
    c4.download_button("Download Supplier Scores Report", dataframe_to_csv_bytes(readable_scores), "supplier_scores_report.csv", "text/csv", use_container_width=True)
    c5, c6 = st.columns(2)
    c5.download_button("Download Allocation Report", dataframe_to_csv_bytes(readable_allocation), "supplier_allocation_report.csv", "text/csv", use_container_width=True)
    c6.download_button("Download Supplier Comparison Report", dataframe_to_csv_bytes(readable_comparison), "supplier_comparison_report.csv", "text/csv", use_container_width=True)
    c7, _ = st.columns(2)
    c7.download_button("Download Supplier Narrative", text_to_bytes(supplier_narrative), "executive_supplier_narrative.txt", "text/plain", use_container_width=True)

    st.subheader("Machine-readable audit outputs")
    c8, c9 = st.columns(2)
    c8.download_button("Decision Audit Data", json_package, "procurement_decision_audit.json", "application/json", use_container_width=True)
    c9.download_button("Supplier 360 Audit Data", supplier_profiles_json, "supplier_360_audit.json", "application/json", use_container_width=True)
    st.caption("Business-readable reports are separated from machine-readable audit data.")

st.markdown("---")
st.caption(f"{BUILD} | Application status: {STATUS} | Human procurement review remains mandatory.")
