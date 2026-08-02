"""Streamlit renderer for governed procurement intelligence outputs."""

import pandas as pd
import streamlit as st


def render_procurement_intelligence(
    decision,
    strategy,
    optimized_allocation,
    negotiation_df,
    risk_result,
    scenario_result,
    executive_narrative,
):
    st.header("Procurement Intelligence")

    st.subheader("Executive Recommendation")
    c1, c2, c3 = st.columns(3)
    c1.metric("Recommended Supplier", decision["recommended_supplier"])
    c2.metric("Award Confidence", f"{decision['award_confidence']}/100")
    c3.metric("Sourcing Strategy", strategy["strategy"])
    st.write(decision["executive_recommendation"])
    st.caption(decision["business_justification"])

    st.subheader("Strategy")
    st.write(f"**Recommendation:** {strategy['strategy']}")
    st.write(strategy["reason"])
    st.write(f"**Recommended term:** {strategy['recommended_term']}")
    st.caption(strategy["governance_note"])

    st.subheader("Governed Multi-Supplier Allocation")
    route_status = optimized_allocation.get("route_status", "UNKNOWN")
    if route_status == "READY":
        st.success("Canonical allocation route completed. Human procurement approval remains mandatory.")
    elif route_status == "WARNING":
        st.warning("Canonical allocation route completed with warnings. Human procurement review is mandatory.")
    else:
        st.error(f"Canonical allocation route is blocked: {route_status}")
    allocation_df = optimized_allocation["allocation_df"]
    if allocation_df.empty:
        st.info("No allocation recommendation is available for this governed route state.")
    else:
        st.dataframe(allocation_df, width="stretch", hide_index=True)
    st.write(optimized_allocation["explanation"])
    for warning in optimized_allocation.get("warnings", ()):
        st.warning(warning)
    for reason in optimized_allocation.get("blocking_reasons", ()):
        st.write(f"- {reason}")
    st.caption(
        "This is a recommendation for human procurement review. It is not an autonomous award, "
        "approval record or ERP authorization."
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
    st.write(f"**Scenario:** {scenario_result['scenario']}")
    st.info(
        "Scenario-specific supplier allocation is deferred until the canonical route is governed for "
        "scenario inputs. No legacy scenario allocation is displayed as an award recommendation."
    )

    st.subheader("AI Explainability 2.0")
    explanation = decision["explainability"]
    st.write(explanation["why_selected"])
    st.write("**Most influential factors:** " + ", ".join(explanation["most_influential_factors"]))
    for competitor in explanation["rejected_suppliers"]:
        st.write(f"- **{competitor['supplier']}**: {competitor['reason']}")
    st.write(f"**Trade-offs:** {explanation['trade_offs']}")
    st.write(f"**Assumptions:** {explanation['assumptions']}")
    st.success(explanation["governance"])

    st.subheader("Executive Decision Narrative")
    st.text_area("Board-ready recommendation", executive_narrative, height=520)
