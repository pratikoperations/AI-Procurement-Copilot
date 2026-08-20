"""Streamlit renderer for governed procurement intelligence outputs."""

import pandas as pd
import streamlit as st

from modules.multi_supplier_allocation_scenario_presenter import build_scenario_presentation


_NON_BLOCKING_GOVERNANCE_MARKERS = (
    "adapter construction is decision support only",
    "allocation is decision support only",
    "controlled synthetic demonstration assumption",
    "feasibility is decision support only",
    "human procurement approval remains mandatory",
    "human procurement review remains mandatory",
    "supplier capacity is supplied evidence and has not been independently verified",
    "not verified supplier evidence",
)


def _split_warning_messages(messages):
    """Separate actionable warnings from retained non-blocking governance evidence."""
    actionable = []
    governance = []
    for raw in messages or ():
        message = str(raw).strip()
        if not message:
            continue
        lowered = message.casefold()
        target = governance if any(marker in lowered for marker in _NON_BLOCKING_GOVERNANCE_MARKERS) else actionable
        if message not in target:
            target.append(message)
    return tuple(actionable), tuple(governance)


def _render_governance_details(*, notes=(), evidence_origin="", scenario_version="", legacy_fallback=False):
    """Keep audit facts available without promoting routine disclosures to alerts."""
    with st.expander("Governance & Evidence Details", expanded=False):
        if notes:
            for note in notes:
                st.write(f"- {note}")
        else:
            st.caption("No additional non-blocking governance notes are recorded for this view.")
        st.write(f"**Evidence origin:** {evidence_origin or 'not available'}")
        if scenario_version:
            st.write(f"**Scenario assumptions:** {scenario_version}")
        st.write("**Human procurement review required:** Yes")
        st.write(f"**Legacy fallback used:** {'Yes' if legacy_fallback else 'No'}")
        st.caption(
            "These records are retained for audit and decision support. They do not create an autonomous award, "
            "approval record or ERP authorization."
        )


def render_procurement_intelligence(
    decision,
    strategy,
    optimized_allocation,
    negotiation_df,
    risk_result,
    scenario_result,
    executive_narrative,
    *,
    recommendation_allowed=True,
):
    st.header("Procurement Intelligence")

    route_status = optimized_allocation.get("route_status", "UNKNOWN")
    allocation_df = optimized_allocation["allocation_df"]
    route_allows_recommendation = route_status in {"READY", "WARNING"} and not allocation_df.empty
    recommendation_allowed = bool(recommendation_allowed and route_allows_recommendation)

    if recommendation_allowed:
        st.subheader("Executive Recommendation")
        c1, c2, c3 = st.columns(3)
        c1.metric("Recommended Supplier", decision["recommended_supplier"])
        c2.metric("Award Confidence", f"{decision['award_confidence']}/100")
        c3.metric("Sourcing Strategy", strategy["strategy"])
        st.write(decision["executive_recommendation"])
        st.caption(decision["business_justification"])
        st.write("**Human procurement approval required.**")

        st.subheader("Strategy")
        st.write(f"**Recommendation:** {strategy['strategy']}")
        st.write(strategy["reason"])
        st.write(f"**Recommended term:** {strategy['recommended_term']}")
        st.caption(strategy["governance_note"])
    else:
        st.subheader("Analytical Procurement View")
        st.error(
            "Supplier award and allocation recommendation language is withheld. Cost, risk, scoring and "
            "supplier analysis remain analytical only."
        )
        st.caption(
            "No supplier has been selected for award. Human procurement review and closure of the listed "
            "blocking controls are required before recommendation language can be used."
        )

    st.subheader("Governed Multi-Supplier Allocation")
    allocation_actionable, allocation_governance = _split_warning_messages(
        optimized_allocation.get("warnings", ())
    )
    if route_status == "READY":
        st.caption("Canonical allocation route completed.")
    elif route_status == "WARNING" and allocation_actionable:
        st.warning("Canonical allocation route completed with review items requiring attention.")
    elif route_status == "WARNING":
        st.caption("Canonical allocation route completed; governance disclosures are available below.")
    else:
        st.error(f"Canonical allocation route is blocked: {route_status}")
    if allocation_df.empty:
        st.info("No allocation recommendation is available for this governed route state.")
    else:
        st.dataframe(allocation_df, width="stretch", hide_index=True)
    st.write(optimized_allocation["explanation"])
    for warning in allocation_actionable:
        st.warning(warning)
    for reason in optimized_allocation.get("blocking_reasons", ()):
        st.write(f"- {reason}")
    _render_governance_details(
        notes=allocation_governance,
        evidence_origin=optimized_allocation.get("evidence_origin") or "",
        legacy_fallback=False,
    )

    st.subheader("Negotiation Intelligence")
    st.dataframe(negotiation_df, width="stretch", hide_index=True)

    st.subheader("Risk Intelligence")
    risk_df = pd.DataFrame(risk_result["risks"])
    r1, r2, r3 = st.columns(3)
    r1.metric("Highest Severity", risk_result["highest_severity"])
    r2.metric("Critical Risks", risk_result["critical_count"])
    r3.metric("High Risks", risk_result["high_count"])
    st.dataframe(risk_df, width="stretch", hide_index=True)

    st.subheader("Scenario Simulation")
    scenario_allocation = scenario_result.get("scenario_allocation")
    if scenario_allocation is None:
        st.error("Canonical scenario allocation evidence is unavailable for this scenario result.")
    else:
        scored = scenario_result.get("scored_df", pd.DataFrame())
        leading_supplier = ""
        leading_score = None
        if not scored.empty:
            leading_supplier = str(scored.iloc[0].get("Supplier", ""))
            leading_score = scored.iloc[0].get("total_score")
        presentation = build_scenario_presentation(
            scenario_allocation,
            analytical_leading_supplier=leading_supplier,
            analytical_leading_score=leading_score,
        )
        st.write(f"**Scenario:** {presentation.scenario}")
        st.write(f"**Applicability:** {'Applicable' if presentation.scenario_applicable else 'Not applicable'}")
        st.write(f"**Canonical route status:** {presentation.route_status}")
        scenario_actionable, scenario_governance = _split_warning_messages(presentation.warnings)
        if presentation.route_status == "READY":
            st.caption("Scenario allocation is available for human procurement review.")
        elif presentation.route_status == "WARNING" and scenario_actionable:
            st.warning("Scenario allocation is available with review items requiring attention.")
        elif presentation.route_status == "WARNING":
            st.caption("Scenario allocation is available; governance disclosures are available below.")
        elif presentation.route_status == "NOT_APPLICABLE":
            st.info(presentation.status_reason)
        else:
            st.error("Scenario allocation is blocked. No supplier award or allocation recommendation is permitted.")
        if presentation.allocation_available:
            st.dataframe(presentation.allocation_df, width="stretch", hide_index=True)
        else:
            st.info("No canonical scenario allocation is available for this route state.")
        if presentation.analytical_leading_supplier:
            st.caption(
                f"Analytical leading supplier: {presentation.analytical_leading_supplier}. "
                "This ranking signal is not an award decision."
            )
        for warning in scenario_actionable:
            st.warning(warning)
        for reason in presentation.blocking_reasons:
            st.write(f"- {reason}")
        _render_governance_details(
            notes=scenario_governance,
            evidence_origin=presentation.evidence_origin,
            scenario_version=presentation.scenario_assumption_version or "not versioned",
            legacy_fallback=presentation.legacy_fallback_used,
        )

    st.subheader("AI Explainability 2.0")
    explanation = decision["explainability"]
    if recommendation_allowed:
        st.write(explanation["why_selected"])
    else:
        st.write("Scoring explainability is retained as analytical evidence; it does not constitute supplier selection.")
    st.write("**Most influential factors:** " + ", ".join(explanation["most_influential_factors"]))
    for competitor in explanation["rejected_suppliers"]:
        st.write(f"- **{competitor['supplier']}**: {competitor['reason']}")
    st.write(f"**Trade-offs:** {explanation['trade_offs']}")
    st.write(f"**Assumptions:** {explanation['assumptions']}")
    st.caption(explanation["governance"])

    st.subheader("Executive Decision Narrative")
    st.text_area("Board-ready analytical narrative", executive_narrative, height=520)
