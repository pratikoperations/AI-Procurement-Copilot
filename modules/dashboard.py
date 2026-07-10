"""Dashboard rendering functions."""

import streamlit as st
import plotly.express as px

from modules.utils import unit_cost, money_usd, money_inr


def render_executive_dashboard(scored_df, assumptions, confidence=None):
    """Render executive dashboard for scored suppliers."""
    st.subheader("Executive Dashboard")

    recommended = scored_df.iloc[0]
    lowest = scored_df.sort_values("Quoted Unit Price USD").iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Category Engine", assumptions["category"])
    c2.metric("Annual Volume", f"{assumptions['annual_volume']:,.0f}")
    c3.metric("Recommended Supplier", recommended["Supplier"])
    c4.metric("Award Confidence", f"{confidence}/100" if confidence is not None else "Pending")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Quoted Price", unit_cost(recommended["Quoted Unit Price USD"], assumptions["display_currency"], assumptions["fx_rate"]))
    c6.metric("TCO Unit Cost", unit_cost(recommended["adjusted_tco_unit_usd"], assumptions["display_currency"], assumptions["fx_rate"]))
    c7.metric("Risk Score", f"{recommended['risk_score']}/100")
    c8.metric("Lowest Quote", lowest["Supplier"])

    if recommended["Supplier"] != lowest["Supplier"]:
        st.warning(
            f"{lowest['Supplier']} has the lowest quote, but {recommended['Supplier']} ranks best after TCO, risk, ESG, and performance adjustment."
        )
    else:
        st.success(f"{recommended['Supplier']} is currently both lowest quote and best-value supplier.")


def render_supplier_snapshot(scored_df):
    """Render scored supplier table and charts."""
    st.header("Supplier RFQ + Decision Snapshot")

    display_cols = [
        "Supplier",
        "Quoted Unit Price USD",
        "scenario_unit_price_usd",
        "adjusted_tco_unit_usd",
        "annual_tco_usd",
        "risk_score",
        "risk_category",
        "performance_score",
        "esg_score",
        "total_score",
    ]
    st.dataframe(scored_df[display_cols], use_container_width=True, hide_index=True)

    fig = px.bar(
        scored_df,
        x="Supplier",
        y=["Quoted Unit Price USD", "adjusted_tco_unit_usd"],
        barmode="group",
        title="Quoted Price vs Risk-Adjusted TCO Unit Cost",
    )
    st.plotly_chart(fig, use_container_width=True)

    fig_score = px.bar(
        scored_df,
        x="Supplier",
        y=["risk_score", "performance_score", "esg_score", "total_score"],
        barmode="group",
        title="Supplier Risk, Performance, ESG, and Total Score",
    )
    st.plotly_chart(fig_score, use_container_width=True)


def render_should_cost_section(should_cost_df, target_unit_cost, assumptions):
    """Render packaging should-cost build-up."""
    st.header("Packaging Should-Cost Model")
    st.metric("Should-Cost Target", unit_cost(target_unit_cost, assumptions["display_currency"], assumptions["fx_rate"]))
    st.dataframe(should_cost_df, use_container_width=True, hide_index=True)

    fig = px.bar(
        should_cost_df,
        x="Component",
        y="Unit Cost USD",
        title="Packaging Should-Cost Component Build-Up",
        text_auto=".4f",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_tco_breakdown(scored_df, assumptions):
    """Render TCO breakdown table."""
    st.header("Advanced TCO Breakdown")
    cols = [
        "Supplier",
        "scenario_unit_price_usd",
        "freight_cost_usd",
        "inventory_cost_usd",
        "working_capital_impact_usd",
        "risk_penalty_usd",
        "lead_time_buffer_usd",
        "adjusted_tco_unit_usd",
        "annual_tco_usd",
    ]
    tco_df = scored_df[cols].copy()
    tco_df["annual_tco_inr"] = tco_df["annual_tco_usd"] * assumptions["fx_rate"]
    st.dataframe(tco_df, use_container_width=True, hide_index=True)


def render_executive_value(value_metrics, assumptions):
    """Render executive value metrics."""
    st.header("Executive Value Breakdown")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Market Quote Gap", money_usd(value_metrics["market_quote_gap_usd"]))
    label = "TCO Savings vs Lowest Quote" if value_metrics["tco_savings_or_premium_vs_lowest_usd"] >= 0 else "TCO Premium vs Lowest Quote"
    c2.metric(label, money_usd(abs(value_metrics["tco_savings_or_premium_vs_lowest_usd"])))
    c3.metric("Risk Score Advantage", f"{value_metrics['risk_score_advantage']} pts")
    c4.metric("EBITDA Opportunity", money_usd(value_metrics["estimated_ebitda_opportunity_usd"]))


def render_allocation(allocation_df, assumptions):
    """Render supplier allocation recommendation."""
    st.header("Constraint-Style Supplier Allocation")
    display = allocation_df.copy()
    display["Estimated Annual TCO INR"] = display["Estimated Annual TCO USD"] * assumptions["fx_rate"]
    st.dataframe(display, use_container_width=True, hide_index=True)

    fig = px.pie(
        display,
        names="Supplier",
        values="Recommended Allocation %",
        title="Recommended Supplier Allocation",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_scenario_table(scenario_df, assumptions):
    """Render scenario stress test results."""
    st.header("Multi-Scenario Stress Test")
    display = scenario_df.copy()
    display["Annual TCO INR"] = display["Annual TCO USD"] * assumptions["fx_rate"]
    st.dataframe(display, use_container_width=True, hide_index=True)

    fig = px.bar(
        display,
        x="Scenario",
        y="Annual TCO USD",
        color="Winning Supplier",
        title="Scenario Stress Test: Winning Supplier and Annual TCO",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_negotiation(playbook_text, negotiation_result):
    """Render negotiation simulator output and playbook."""
    st.header("Negotiation Simulator + Playbook")
    c1, c2, c3 = st.columns(3)
    c1.metric("Current TCO Unit", money_usd(negotiation_result["current_tco_unit_usd"]))
    c2.metric("Simulated TCO Unit", money_usd(negotiation_result["simulated_tco_unit_usd"]))
    c3.metric("Annual TCO Saving", money_usd(negotiation_result["annual_saving_usd"]))
    st.text_area("Generated negotiation playbook", playbook_text, height=360)
