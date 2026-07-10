"""Dashboard rendering functions."""

import streamlit as st
import plotly.express as px

from modules.utils import money_usd, money_inr, unit_cost


def render_executive_dashboard(scored_df, assumptions):
    """Render executive dashboard for scored suppliers."""
    st.subheader("Executive Dashboard")

    recommended = scored_df.iloc[0]
    lowest = scored_df.sort_values("Quoted Unit Price USD").iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Category Engine", assumptions["category"])
    c2.metric("Annual Volume", f"{assumptions['annual_volume']:,.0f}")
    c3.metric("Recommended Supplier", recommended["Supplier"])
    c4.metric("Weighted Score", f"{recommended['total_score']}/100")

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
