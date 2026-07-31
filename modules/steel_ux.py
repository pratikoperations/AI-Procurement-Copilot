"""C3.6/C3.7 governed Steel UX, state, and export integration."""

from __future__ import annotations

import math
from typing import Mapping, MutableMapping

import pandas as pd
import streamlit as st

from modules.steel_exports import build_steel_excel_workbook, build_steel_governance_manifest, build_steel_json_export
from modules.steel_scenario import STEEL_SCENARIOS, run_governed_steel_scenarios

STEEL_PROFILES = ("CR_COIL_COMMERCIAL", "GI_COIL_Z120", "PPGI_COIL_Z120")
DISPLAY_MODES = ("USD", "INR", "Both")
SOURCING_ROUTES = ("Domestic", "Import")
SUBSTITUTION_STATES = ("Non-applicable", "Approved", "Conditional", "Pending", "Rejected")
STEEL_STATE_DEFAULTS = {
    "steel_profile": "CR_COIL_COMMERCIAL", "steel_zinc_cost_usd_per_kg": 0.0,
    "steel_paint_treatment_usd_per_kg": 0.0, "steel_sourcing_route": "Domestic",
    "steel_import_duty_pct": 0.0, "steel_substitution_status": "Non-applicable",
    "steel_scenario": "Base Case",
}


def normalize_steel_dependent_state(values: Mapping) -> dict:
    state = dict(STEEL_STATE_DEFAULTS)
    state.update(values or {})
    profile, route = state["steel_profile"], state["steel_sourcing_route"]
    display = state.get("display_currency", "Both")
    if profile not in STEEL_PROFILES:
        raise ValueError(f"Unsupported Steel profile '{profile}'.")
    if route not in SOURCING_ROUTES:
        raise ValueError(f"Unsupported Steel sourcing route '{route}'.")
    if display not in DISPLAY_MODES:
        raise ValueError(f"Unsupported Steel display mode '{display}'.")

    def number(key):
        value = state.get(key)
        if value is None or isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{key} must be a finite numeric value.")
        value = float(value)
        if not math.isfinite(value) or value < 0:
            raise ValueError(f"{key} has an invalid governed value.")
        return value

    zinc, paint, duty = number("steel_zinc_cost_usd_per_kg"), number("steel_paint_treatment_usd_per_kg"), number("steel_import_duty_pct")
    if profile == "CR_COIL_COMMERCIAL":
        zinc, paint = 0.0, 0.0
    elif profile == "GI_COIL_Z120":
        zinc, paint = zinc if zinc > 0 else 0.08, 0.0
    else:
        zinc, paint = zinc if zinc > 0 else 0.08, paint if paint > 0 else 0.12
    duty = 0.0 if route == "Domestic" else (duty if duty > 0 else 10.0)
    substitution = str(state.get("steel_substitution_status", "Non-applicable"))
    scenario = str(state.get("steel_scenario", "Base Case"))
    if substitution not in SUBSTITUTION_STATES:
        raise ValueError(f"Unsupported Steel substitution state '{substitution}'.")
    if scenario not in STEEL_SCENARIOS:
        raise ValueError(f"Unsupported Steel scenario '{scenario}'.")
    state.update({"steel_zinc_cost_usd_per_kg": zinc, "steel_paint_treatment_usd_per_kg": paint, "steel_import_duty_pct": duty, "steel_substitution_status": substitution, "steel_scenario": scenario})
    return state


def apply_steel_state_transition(session_state: MutableMapping, profile: str, route: str) -> dict:
    values = dict(session_state)
    values.update({"steel_profile": profile, "steel_sourcing_route": route})
    normalized = normalize_steel_dependent_state(values)
    for key in STEEL_STATE_DEFAULTS:
        session_state[key] = normalized[key]
    return normalized


def _render_controls(assumptions: Mapping) -> dict:
    for key, value in STEEL_STATE_DEFAULTS.items():
        st.session_state.setdefault(key, value)
    current = normalize_steel_dependent_state({**assumptions, **st.session_state})
    for key in STEEL_STATE_DEFAULTS:
        st.session_state[key] = current[key]
    with st.sidebar.expander("Steel Decision Controls", expanded=True):
        st.caption("Controlled synthetic C3 assumptions; not live market data or technical certification.")
        profile = st.selectbox("Steel Profile", STEEL_PROFILES, key="steel_profile")
        route = st.selectbox("Sourcing Route", SOURCING_ROUTES, key="steel_sourcing_route")
        apply_steel_state_transition(st.session_state, profile, route)
        profile, route = st.session_state["steel_profile"], st.session_state["steel_sourcing_route"]
        st.number_input("Zinc Cost USD/kg", min_value=0.0, step=0.01, key="steel_zinc_cost_usd_per_kg", disabled=profile == "CR_COIL_COMMERCIAL")
        st.number_input("Paint / Treatment Cost USD/kg", min_value=0.0, step=0.01, key="steel_paint_treatment_usd_per_kg", disabled=profile != "PPGI_COIL_Z120")
        st.number_input("Import Duty %", min_value=0.0, max_value=100.0, step=1.0, key="steel_import_duty_pct", disabled=route == "Domestic")
        st.selectbox("Substitution State", SUBSTITUTION_STATES, key="steel_substitution_status")
        st.selectbox("Governed Scenario", STEEL_SCENARIOS, key="steel_scenario")
        st.caption("Annual volume is entered in kg. Metric-tonne reporting is informational only.")
    normalized = normalize_steel_dependent_state({**assumptions, **st.session_state})
    for key in STEEL_STATE_DEFAULTS:
        st.session_state[key] = normalized[key]
    return normalized


def _display_allocation(frame: pd.DataFrame, display_mode: str) -> pd.DataFrame:
    columns = ["Supplier", "Technical Eligible", "Allocated Volume kg", "Allocation %", "Supplier Capacity kg"]
    if display_mode in {"USD", "Both"}:
        columns += ["Normalized USD/kg", "Annual Value USD"]
    if display_mode in {"INR", "Both"}:
        columns += ["Equivalent INR/kg", "Annual Value INR"]
    return frame[[column for column in columns if column in frame.columns]].copy()


def render_steel_governed_dashboard(suppliers: pd.DataFrame, assumptions: Mapping) -> None:
    """Render the isolated Steel route, then stop before generic downstream outputs."""
    state = _render_controls(assumptions)
    profile, volume = state["steel_profile"], float(assumptions["annual_volume"])
    fx, display_mode = float(assumptions["fx_rate"]), assumptions.get("display_currency", "Both")
    summary, details = run_governed_steel_scenarios(
        suppliers, profile, volume, fx, display_mode,
        cost_assumptions={"zinc_cost_usd_per_kg": state["steel_zinc_cost_usd_per_kg"], "paint_treatment_usd_per_kg": state["steel_paint_treatment_usd_per_kg"], "sourcing_route": state["steel_sourcing_route"], "import_duty_pct": state["steel_import_duty_pct"]},
        scenario_assumptions={"grade_substitution_status": state["steel_substitution_status"]},
    )
    selected = details[state["steel_scenario"]]
    scored, recommendation = selected["scored_suppliers"], selected["recommendation"]
    standard, optimized = selected["standard_allocation"], selected["optimized_allocation"]

    st.header("Governed Steel Decision Support")
    st.warning("Controlled synthetic demonstration only. No live market-data claim, engineering approval, metallurgical certification, autonomous award, production allocation or realised-savings claim.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Selected Profile", profile); c2.metric("Annual Volume", f"{volume:,.0f} kg"); c3.metric("Metric Tonnes", f"{volume / 1000:,.1f} MT"); c4.metric("Eligible Suppliers", int(scored["technical_eligible"].sum()))
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Governed Winner", recommendation.get("winner") or "No winner"); d2.metric("Winner State", recommendation["winner_state"]); d3.metric("Unallocated Volume", f"{optimized.attrs['unallocated_volume_kg']:,.0f} kg"); d4.metric("Human Approval", "Required")

    columns = ["Supplier", "technical_eligible", "normalized_usd_per_kg", "equivalent_inr_per_kg", "generic_risk_score", "steel_risk_score", "governed_total_score", "governed_rank", "eligibility_failure_reasons"]
    decision = scored[[c for c in columns if c in scored.columns]].copy().rename(columns={"technical_eligible": "Technical Eligibility", "normalized_usd_per_kg": "Normalized USD/kg", "equivalent_inr_per_kg": "Equivalent INR/kg", "generic_risk_score": "Generic Supplier Risk", "steel_risk_score": "Steel-Specific Risk", "governed_total_score": "Governed Total Score", "governed_rank": "Governed Rank", "eligibility_failure_reasons": "Eligibility Failure Reasons"})
    if display_mode == "USD": decision = decision.drop(columns=["Equivalent INR/kg"], errors="ignore")
    if display_mode == "INR": decision = decision.drop(columns=["Normalized USD/kg"], errors="ignore")
    st.subheader("Supplier Comparison"); st.dataframe(decision, width="stretch", hide_index=True)
    st.subheader("Standard Allocation"); st.dataframe(_display_allocation(standard, display_mode), width="stretch", hide_index=True); st.caption(f"Unallocated volume: {standard.attrs['unallocated_volume_kg']:,.0f} kg")
    st.subheader("Optimized Allocation"); st.dataframe(_display_allocation(optimized, display_mode), width="stretch", hide_index=True); st.caption(f"Unallocated volume: {optimized.attrs['unallocated_volume_kg']:,.0f} kg")
    st.subheader("Seven Governed Scenarios"); st.dataframe(summary, width="stretch", hide_index=True)

    manifest = build_steel_governance_manifest(state, summary, selected, fx, display_mode)
    excel_bytes = build_steel_excel_workbook(state, summary, selected, manifest)
    json_bytes = build_steel_json_export(manifest)
    st.subheader("Governed Steel Downloads")
    e1, e2 = st.columns(2)
    e1.download_button("Download Steel Excel Analysis", excel_bytes, "governed_steel_analysis.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    e2.download_button("Download Steel Decision Audit JSON", json_bytes, "governed_steel_decision_audit.json", "application/json", use_container_width=True)
    st.info("Recommendation remains pending human approval. No autonomous award is performed.")
    st.caption("Grade-substitution states are workflow evidence only and do not provide engineering approval.")
    st.stop()
