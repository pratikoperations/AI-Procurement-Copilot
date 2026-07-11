"""Dashboard rendering functions."""

import streamlit as st
import plotly.express as px

from modules.utils import unit_cost, money_usd


SUPPLIER_SNAPSHOT_LABELS = {
    "scenario_unit_price_usd": "Scenario Unit Price (USD)",
    "adjusted_tco_unit_usd": "Risk-Adjusted TCO (USD)",
    "annual_tco_usd": "Annual TCO (USD)",
    "risk_score": "Risk Resilience Score",
    "risk_category": "Risk Category",
    "performance_score": "Performance",
    "esg_score": "ESG Maturity",
    "total_score": "Overall Decision Score",
}

TCO_LABELS = {
    "scenario_unit_price_usd": "Scenario Unit Price (USD)",
    "freight_cost_usd": "Freight Cost (USD)",
    "inventory_cost_usd": "Inventory Cost (USD)",
    "working_capital_impact_usd": "Working-Capital Impact (USD)",
    "risk_penalty_usd": "Risk Penalty (USD)",
    "lead_time_buffer_usd": "Lead-Time Buffer (USD)",
    "adjusted_tco_unit_usd": "Risk-Adjusted TCO (USD)",
    "annual_tco_usd": "Annual TCO (USD)",
    "annual_tco_inr": "Annual TCO (INR)",
}

SCENARIO_ANNUAL_TCO_CANDIDATES = (
    "Annual TCO (USD)",
    "Annual TCO USD",
    "annual_tco_usd",
)

SCENARIO_SUPPLIER_CANDIDATES = (
    "Winning Supplier",
    "Supplier",
)


def resolve_scenario_column(columns, candidates, field_name):
    """Resolve a governed scenario column while retaining backward compatibility."""
    for candidate in candidates:
        if candidate in columns:
            return candidate
    raise KeyError(
        f"Scenario output is missing required {field_name}. "
        f"Expected one of: {', '.join(candidates)}"
    )


def render_executive_dashboard(scored_df, assumptions, confidence=None):
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
    c7.metric("Risk Resilience Score", f"{recommended['risk_score']}/100")
    c8.metric("Lowest Quote", lowest["Supplier"])

    if recommended["Supplier"] != lowest["Supplier"]:
        st.warning(f"{lowest['Supplier']} has the lowest quote, but {recommended['Supplier']} ranks best after TCO, risk resilience, ESG, and performance adjustment.")
    else:
        st.success(f"{recommended['Supplier']} is currently both the lowest quote and the best-value supplier.")


def render_supplier_snapshot(scored_df):
    st.header("Supplier RFQ Decision Snapshot")
    display_cols = [
        "Supplier", "Quoted Unit Price USD", "scenario_unit_price_usd",
        "adjusted_tco_unit_usd", "annual_tco_usd", "risk_score",
        "risk_category", "performance_score", "esg_score", "total_score",
    ]
    st.dataframe(scored_df[display_cols].rename(columns=SUPPLIER_SNAPSHOT_LABELS), width="stretch", hide_index=True)

    price_chart_df = scored_df.rename(columns={
        "Quoted Unit Price USD": "Quoted Price",
        "adjusted_tco_unit_usd": "Risk-Adjusted TCO",
    })
    fig = px.bar(
        price_chart_df,
        x="Supplier",
        y=["Quoted Price", "Risk-Adjusted TCO"],
        barmode="group",
        title="Quoted Price vs Risk-Adjusted TCO Unit Cost",
        labels={"value": "Unit Cost (USD)", "variable": "Cost Measure"},
    )
    fig.update_layout(legend_title_text="Cost Measure", margin=dict(l=10, r=10, t=55, b=10))
    st.plotly_chart(fig, width="stretch")

    score_chart_df = scored_df.rename(columns={
        "risk_score": "Risk Resilience Score",
        "performance_score": "Performance",
        "esg_score": "ESG Maturity",
        "total_score": "Overall Decision Score",
    })
    fig_score = px.bar(
        score_chart_df,
        x="Supplier",
        y=["Risk Resilience Score", "Performance", "ESG Maturity", "Overall Decision Score"],
        barmode="group",
        title="Supplier Risk Resilience, Performance, ESG, and Overall Decision Score",
        labels={"value": "Score (0–100)", "variable": "Decision Dimension"},
        range_y=[0, 100],
    )
    fig_score.update_layout(legend_title_text="Decision Dimension", margin=dict(l=10, r=10, t=55, b=10))
    st.plotly_chart(fig_score, width="stretch")


def render_should_cost_section(should_cost_df, target_unit_cost, assumptions):
    category = assumptions.get("category", "Packaging Procurement")
    commodity = assumptions.get("commodity", "Category")
    heading = "Packaging Should-Cost Model" if category == "Packaging Procurement" else "Raw Material Should-Cost Model"
    chart_title = "Packaging Should-Cost Component Build-Up" if category == "Packaging Procurement" else f"{commodity} Should-Cost Component Build-Up"
    st.header(heading)
    st.metric("Should-Cost Target", unit_cost(target_unit_cost, assumptions["display_currency"], assumptions["fx_rate"]))
    st.dataframe(should_cost_df, width="stretch", hide_index=True)
    fig = px.bar(should_cost_df, x="Component", y="Unit Cost USD", title=chart_title, text_auto=".4f", labels={"Unit Cost USD": "Unit Cost (USD)"})
    fig.update_layout(margin=dict(l=10, r=10, t=55, b=10))
    st.plotly_chart(fig, width="stretch")


def render_tco_breakdown(scored_df, assumptions):
    st.header("Advanced TCO Breakdown")
    cols = [
        "Supplier", "scenario_unit_price_usd", "freight_cost_usd",
        "inventory_cost_usd", "working_capital_impact_usd", "risk_penalty_usd",
        "lead_time_buffer_usd", "adjusted_tco_unit_usd", "annual_tco_usd",
    ]
    tco_df = scored_df[cols].copy()
    tco_df["annual_tco_inr"] = tco_df["annual_tco_usd"] * assumptions["fx_rate"]
    st.dataframe(tco_df.rename(columns=TCO_LABELS), width="stretch", hide_index=True)


def render_executive_value(value_metrics, assumptions):
    st.header("Executive Value Breakdown")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Market Quote Gap", money_usd(value_metrics["market_quote_gap_usd"]))
    label = "TCO Savings vs Lowest Quote" if value_metrics["tco_savings_or_premium_vs_lowest_usd"] >= 0 else "TCO Premium vs Lowest Quote"
    c2.metric(label, money_usd(abs(value_metrics["tco_savings_or_premium_vs_lowest_usd"])))
    c3.metric("Risk Resilience Advantage", f"{value_metrics['risk_score_advantage']} pts")
    c4.metric("EBITDA Opportunity", money_usd(value_metrics["estimated_ebitda_opportunity_usd"]))


def render_allocation(allocation_df, assumptions):
    st.header("Recommended Supplier Allocation")
    display = allocation_df.copy()
    display["Estimated Annual TCO INR"] = display["Estimated Annual TCO USD"] * assumptions["fx_rate"]
    st.dataframe(display, width="stretch", hide_index=True)
    fig = px.pie(display, names="Supplier", values="Recommended Allocation %", title="Recommended Supplier Allocation")
    fig.update_layout(margin=dict(l=10, r=10, t=55, b=10))
    st.plotly_chart(fig, width="stretch")


def render_scenario_table(scenario_df, assumptions):
    st.header("Multi-Scenario Stress Test")
    display = scenario_df.copy()

    annual_tco_column = resolve_scenario_column(
        display.columns,
        SCENARIO_ANNUAL_TCO_CANDIDATES,
        "annual TCO column",
    )
    supplier_column = resolve_scenario_column(
        display.columns,
        SCENARIO_SUPPLIER_CANDIDATES,
        "supplier column",
    )

    display["Annual TCO (INR)"] = display[annual_tco_column] * assumptions["fx_rate"]
    st.dataframe(display, width="stretch", hide_index=True)

    fig = px.bar(
        display,
        x="Scenario",
        y=annual_tco_column,
        color=supplier_column,
        title="Scenario Stress Test: Winning Supplier and Annual TCO",
        labels={annual_tco_column: "Annual TCO (USD)", supplier_column: "Winning Supplier"},
    )
    fig.update_layout(legend_title_text="Winning Supplier", margin=dict(l=10, r=10, t=55, b=10))
    st.plotly_chart(fig, width="stretch")


def render_negotiation(playbook_text, negotiation_result):
    st.header("Negotiation Simulator and Playbook")
    c1, c2, c3 = st.columns(3)
    c1.metric("Current TCO Unit", money_usd(negotiation_result["current_tco_unit_usd"]))
    c2.metric("Simulated TCO Unit", money_usd(negotiation_result["simulated_tco_unit_usd"]))
    c3.metric("Annual TCO Saving", money_usd(negotiation_result["annual_saving_usd"]))
    st.text_area("Generated negotiation playbook", playbook_text, height=360)
