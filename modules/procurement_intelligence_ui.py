"""Streamlit renderer for Build 0.9.3 procurement intelligence outputs."""

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

    st.subheader("Optimized Allocation")
    st.dataframe(optimized_allocation["allocation_df"], width="stretch", hide_index=True)
    st.write(optimized_allocation["explanation"])

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
    st.write(
        f"Recommended supplier under scenario: **{scenario_result['decision']['recommended_supplier']}** "
        f"with confidence **{scenario_result['decision']['award_confidence']}/100**."
    )
    st.dataframe(
        scenario_result["allocation"]["allocation_df"],
        width="stretch",
        hide_index=True,
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
