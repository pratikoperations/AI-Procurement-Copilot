"""Dashboard rendering functions with governed display-currency handling."""

import plotly.express as px
import streamlit as st

from modules.c1_ux import technical_eligibility_label
from modules.steel_ux import render_steel_governed_dashboard
from modules.unit_display import format_annual_volume, quantity_basis_caption
from modules.utils import (
    build_currency_display_frame,
    format_money,
    normalize_display_currency,
    unit_cost,
)

NON_CURRENCY_LABELS = {
    "risk_score": "Risk Resilience Score",
    "risk_category": "Risk Category",
    "performance_score": "Performance",
    "esg_score": "ESG Maturity",
    "total_score": "Overall Decision Score",
}
SCENARIO_ANNUAL_TCO_CANDIDATES = ("Annual TCO (USD)", "Annual TCO USD", "annual_tco_usd")
SCENARIO_SUPPLIER_CANDIDATES = ("Winning Supplier", "Supplier")
C2_SYNTHETIC_DISCLOSURE = (
    "Flexible Laminates capability, continuity, scenario and tooling values are synthetic controlled "
    "demonstration assumptions. They are not audited supplier evidence, laboratory results, technical "
    "certification, market forecasts or production-readiness claims."
)


def _display_settings(assumptions=None):
    values = assumptions or {}
    return normalize_display_currency(values.get("display_currency", "USD")), float(values.get("fx_rate", 83))


def _chart_currency(currency):
    return "INR" if normalize_display_currency(currency) == "INR" else "USD"


def _quantity_basis(assumptions=None):
    values = assumptions or {}
    return quantity_basis_caption(values.get("annual_volume", 0), values.get("annual_volume_unit", "unit"))


def is_flexible_laminate_context(assumptions=None):
    values = assumptions or {}
    return values.get("category") == "Packaging Procurement" and values.get("commodity") == "Flexible Laminates"


def is_steel_context(assumptions=None):
    values = assumptions or {}
    return values.get("category") == "Raw Material Procurement" and values.get("commodity") == "Steel"


def build_flexible_laminate_context(assumptions):
    """Return stable C2 context shown in the UI and reused by export tests."""
    return {
        "Selected Laminate Structure": assumptions.get("laminate_structure", "Not selected"),
        "Commercial Basis": "kg",
        "Comparison Unit": "USD/kg",
        "Total Micron": assumptions.get("laminate_total_micron", "Not assessed"),
        "Micron Governance": "Metadata only; not used to infer layer mass, density, barrier or technical compliance.",
        "Confidence Governance": "Controlled decision-governance indicator; not predictive accuracy.",
        "Synthetic Assumption Disclosure": C2_SYNTHETIC_DISCLOSURE,
    }


def build_supplier_snapshot_display(scored_df, assumptions=None):
    currency, fx_rate = _display_settings(assumptions)
    base_cols = [
        "Supplier", "Quoted Unit Price USD", "scenario_unit_price_usd",
        "adjusted_tco_unit_usd", "annual_tco_usd", "technical_eligible",
        "risk_score", "risk_category", "performance_score", "esg_score", "total_score",
    ]
    if is_flexible_laminate_context(assumptions):
        base_cols += [
            "technical_ineligibility_reasons", "generic_failure_probability",
            "laminate_failure_probability", "generic_risk_penalty_usd",
            "laminate_risk_penalty_usd", "combined_risk_penalty_usd",
        ]
    if is_steel_context(assumptions):
        base_cols += [
            "normalized_usd_per_kg", "equivalent_inr_per_kg", "generic_risk_score",
            "steel_risk_score", "governed_total_score", "governed_rank",
            "eligibility_failure_reasons",
        ]
    display = scored_df[[column for column in base_cols if column in scored_df.columns]].copy()
    if "technical_eligible" in display.columns:
        display["technical_eligible"] = display["technical_eligible"].map(technical_eligibility_label)
    display = display.rename(columns={
        **NON_CURRENCY_LABELS,
        "technical_eligible": "Technical Eligibility",
        "technical_ineligibility_reasons": "Technical Ineligibility Reasons",
        "generic_failure_probability": "Generic Failure Probability",
        "laminate_failure_probability": "Laminate Failure Probability",
        "generic_risk_penalty_usd": "Generic Risk Penalty USD/kg",
        "laminate_risk_penalty_usd": "Laminate Risk Penalty USD/kg",
        "combined_risk_penalty_usd": "Combined Risk Penalty USD/kg",
        "generic_risk_score": "Generic Supplier Risk",
        "steel_risk_score": "Steel-Specific Risk",
        "governed_total_score": "Governed Steel Score",
        "governed_rank": "Governed Rank",
        "eligibility_failure_reasons": "Eligibility Failure Reasons",
    })
    currency_mapping = {
        "Quoted Unit Price USD": "Quoted Unit Price",
        "scenario_unit_price_usd": "Scenario Unit Price",
        "adjusted_tco_unit_usd": "Risk-Adjusted TCO",
        "annual_tco_usd": "Annual TCO",
    }
    return build_currency_display_frame(display, currency_mapping, currency, fx_rate)


def build_should_cost_display(should_cost_df, assumptions=None):
    """Return a display-only should-cost frame without mutating authoritative values."""
    currency, fx_rate = _display_settings(assumptions)
    return build_currency_display_frame(
        should_cost_df,
        {"Unit Cost USD": "Unit Cost"},
        currency,
        fx_rate,
    )


def build_should_cost_column_config(display):
    """Return explicit compact columns so component values remain visible on narrow viewports."""
    config = {
        "Component": st.column_config.TextColumn(
            "Component",
            width="small",
            help="Should-cost component from the authoritative category engine.",
        )
    }
    if "Unit Cost (USD)" in display.columns:
        config["Unit Cost (USD)"] = st.column_config.NumberColumn(
            "Unit Cost (USD)",
            format="$%.4f",
            width="small",
        )
    if "Unit Cost (INR)" in display.columns:
        config["Unit Cost (INR)"] = st.column_config.NumberColumn(
            "Unit Cost (INR)",
            format="₹%.2f",
            width="small",
        )
    return config


def resolve_scenario_column(columns, candidates, field_name):
    for candidate in candidates:
        if candidate in columns:
            return candidate
    raise KeyError(f"Scenario output is missing required {field_name}. Expected one of: {', '.join(candidates)}")


def render_executive_dashboard(scored_df, assumptions, confidence=None):
    st.subheader("Executive Dashboard")
    if is_steel_context(assumptions):
        render_steel_governed_dashboard(scored_df, assumptions)
        return
    recommended = scored_df.iloc[0]
    lowest = scored_df.sort_values("Quoted Unit Price USD").iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Category Engine", assumptions["category"])
    c2.metric("Annual Volume", format_annual_volume(assumptions["annual_volume"], assumptions.get("annual_volume_unit", "unit")))
    c3.metric("Recommended Supplier", recommended["Supplier"])
    c4.metric("Award Confidence", f"{confidence}/100" if confidence is not None else "Pending")
    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Quoted Price", unit_cost(recommended["Quoted Unit Price USD"], assumptions["display_currency"], assumptions["fx_rate"]))
    c6.metric("TCO Unit Cost", unit_cost(recommended["adjusted_tco_unit_usd"], assumptions["display_currency"], assumptions["fx_rate"]))
    c7.metric("Risk Resilience Score", f"{recommended['risk_score']}/100")
    c8.metric("Lowest Quote", lowest["Supplier"])
    if is_flexible_laminate_context(assumptions):
        context = build_flexible_laminate_context(assumptions)
        st.info(f"Structure: {context['Selected Laminate Structure']} | Basis: kg | Comparison: USD/kg | Total micron: {context['Total Micron']} (metadata only)")
        st.caption(context["Confidence Governance"])
        st.warning(context["Synthetic Assumption Disclosure"])
    if recommended["Supplier"] != lowest["Supplier"]:
        st.warning(f"{lowest['Supplier']} has the lowest quote, but {recommended['Supplier']} ranks best after TCO, risk resilience, ESG, and performance adjustment.")
    else:
        st.success(f"{recommended['Supplier']} is currently both the lowest quote and the best-value supplier.")


def render_supplier_snapshot(scored_df, assumptions=None):
    st.header("Supplier RFQ Decision Snapshot")
    st.caption(_quantity_basis(assumptions))
    display = build_supplier_snapshot_display(scored_df, assumptions)
    st.dataframe(display, width="stretch", hide_index=True)
    currency, fx_rate = _display_settings(assumptions)
    chart_currency = _chart_currency(currency)
    multiplier = fx_rate if chart_currency == "INR" else 1
    price_chart_df = scored_df[["Supplier", "Quoted Unit Price USD", "adjusted_tco_unit_usd"]].copy()
    price_chart_df["Quoted Price"] = price_chart_df["Quoted Unit Price USD"] * multiplier
    price_chart_df["Risk-Adjusted TCO"] = price_chart_df["adjusted_tco_unit_usd"] * multiplier
    fig = px.bar(price_chart_df, x="Supplier", y=["Quoted Price", "Risk-Adjusted TCO"], barmode="group", title="Quoted Price vs Risk-Adjusted TCO Unit Cost", labels={"value": f"Unit Cost ({chart_currency})", "variable": "Cost Measure"})
    fig.update_layout(legend_title_text="Cost Measure", margin=dict(l=10, r=10, t=55, b=10))
    st.plotly_chart(fig, width="stretch")
    score_chart_df = scored_df.rename(columns={"risk_score": "Risk Resilience Score", "performance_score": "Performance", "esg_score": "ESG Maturity", "total_score": "Overall Decision Score"})
    fig_score = px.bar(score_chart_df, x="Supplier", y=["Risk Resilience Score", "Performance", "ESG Maturity", "Overall Decision Score"], barmode="group", title="Supplier Risk Resilience, Performance, ESG, and Overall Decision Score", labels={"value": "Score (0–100)", "variable": "Decision Dimension"}, range_y=[0, 100])
    fig_score.update_layout(legend_title_text="Decision Dimension", margin=dict(l=10, r=10, t=55, b=10))
    st.plotly_chart(fig_score, width="stretch")


def render_should_cost_section(should_cost_df, target_unit_cost, assumptions):
    category = assumptions.get("category", "Packaging Procurement")
    commodity = assumptions.get("commodity", "Category")
    currency, fx_rate = _display_settings(assumptions)
    heading = "Packaging Should-Cost Model" if category == "Packaging Procurement" else "Raw Material Should-Cost Model"
    chart_title = "Packaging Should-Cost Component Build-Up" if category == "Packaging Procurement" else f"{commodity} Should-Cost Component Build-Up"
    st.header(heading)
    st.metric("Should-Cost Target", unit_cost(target_unit_cost, currency, fx_rate))
    display = build_should_cost_display(should_cost_df, assumptions)
    st.dataframe(
        display,
        width="stretch",
        hide_index=True,
        column_order=list(display.columns),
        column_config=build_should_cost_column_config(display),
    )
    chart_currency = _chart_currency(currency)
    chart_df = should_cost_df.copy()
    chart_column = f"Unit Cost ({chart_currency})"
    chart_df[chart_column] = chart_df["Unit Cost USD"] * (fx_rate if chart_currency == "INR" else 1)
    fig = px.bar(chart_df, x="Component", y=chart_column, title=chart_title, text_auto=".4f", labels={chart_column: chart_column})
    fig.update_layout(margin=dict(l=10, r=10, t=55, b=10))
    st.plotly_chart(fig, width="stretch")


def render_tco_breakdown(scored_df, assumptions):
    st.header("Advanced TCO Breakdown")
    currency, fx_rate = _display_settings(assumptions)
    cols = ["Supplier", "scenario_unit_price_usd", "freight_cost_usd", "inventory_cost_usd", "working_capital_impact_usd", "risk_penalty_usd", "lead_time_buffer_usd", "adjusted_tco_unit_usd", "annual_tco_usd"]
    if is_flexible_laminate_context(assumptions):
        cols += ["generic_risk_penalty_usd", "laminate_risk_penalty_usd", "combined_risk_penalty_usd"]
    source = scored_df[[column for column in cols if column in scored_df.columns]].copy()
    mapping = {"scenario_unit_price_usd": "Scenario Unit Price", "freight_cost_usd": "Freight Cost", "inventory_cost_usd": "Inventory Cost", "working_capital_impact_usd": "Working-Capital Impact", "risk_penalty_usd": "Risk Penalty", "lead_time_buffer_usd": "Lead-Time Buffer", "adjusted_tco_unit_usd": "Risk-Adjusted TCO", "annual_tco_usd": "Annual TCO", "generic_risk_penalty_usd": "Generic Risk Penalty", "laminate_risk_penalty_usd": "Laminate Risk Penalty", "combined_risk_penalty_usd": "Combined Risk Penalty"}
    st.dataframe(build_currency_display_frame(source, mapping, currency, fx_rate), width="stretch", hide_index=True)


def render_executive_value(value_metrics, assumptions):
    st.header("Executive Value Breakdown")
    currency, fx_rate = _display_settings(assumptions)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Market Quote Gap", format_money(value_metrics["market_quote_gap_usd"], currency, fx_rate))
    label = "TCO Savings vs Lowest Quote" if value_metrics["tco_savings_or_premium_vs_lowest_usd"] >= 0 else "TCO Premium vs Lowest Quote"
    c2.metric(label, format_money(abs(value_metrics["tco_savings_or_premium_vs_lowest_usd"]), currency, fx_rate))
    c3.metric("Risk Resilience Advantage", f"{value_metrics['risk_score_advantage']} pts")
    c4.metric("EBITDA Opportunity", format_money(value_metrics["estimated_ebitda_opportunity_usd"], currency, fx_rate))


def render_allocation(allocation_df, assumptions):
    st.header("Recommended Supplier Allocation")
    st.caption(_quantity_basis(assumptions))
    if allocation_df.empty:
        st.warning("No allocation — no supplier satisfies the governed allocation conditions.")
        return
    currency, fx_rate = _display_settings(assumptions)
    display = build_currency_display_frame(allocation_df.copy(), {"Estimated Annual TCO USD": "Estimated Annual TCO"}, currency, fx_rate)
    st.dataframe(display, width="stretch", hide_index=True)
    fig = px.pie(display, names="Supplier", values="Recommended Allocation %", title="Recommended Supplier Allocation")
    fig.update_layout(margin=dict(l=10, r=10, t=55, b=10))
    st.plotly_chart(fig, width="stretch")


def render_scenario_table(scenario_df, assumptions):
    st.header("Multi-Scenario Stress Test")
    st.caption(_quantity_basis(assumptions))
    currency, fx_rate = _display_settings(assumptions)
    annual_tco_column = resolve_scenario_column(scenario_df.columns, SCENARIO_ANNUAL_TCO_CANDIDATES, "annual TCO column")
    supplier_column = resolve_scenario_column(scenario_df.columns, SCENARIO_SUPPLIER_CANDIDATES, "supplier column")
    display = build_currency_display_frame(scenario_df.copy(), {annual_tco_column: "Annual TCO"}, currency, fx_rate)
    st.dataframe(display, width="stretch", hide_index=True)
    if is_flexible_laminate_context(assumptions):
        tooling = scenario_df.loc[scenario_df["Scenario"] == "Tooling Replacement Scenario"]
        if not tooling.empty and "Tooling Replacement Applied" in tooling.columns:
            row = tooling.iloc[0]
            if int(row["Tooling Replacement Applied"]) == 0 and int(row.get("Already New Tooling", 0)) > 0:
                st.info("No replacement applied — suppliers already use new-tooling economics.")
        st.caption("Confidence is a controlled governance indicator, not predictive accuracy.")
        st.warning(C2_SYNTHETIC_DISCLOSURE)
    chart_currency = _chart_currency(currency)
    chart_df = scenario_df.dropna(subset=[annual_tco_column]).copy()
    if chart_df.empty:
        return
    chart_column = f"Annual TCO ({chart_currency})"
    chart_df[chart_column] = chart_df[annual_tco_column] * (fx_rate if chart_currency == "INR" else 1)
    fig = px.bar(chart_df, x="Scenario", y=chart_column, color=supplier_column, title="Scenario Stress Test: Winning Supplier and Annual TCO", labels={chart_column: chart_column, supplier_column: "Winning Supplier"})
    fig.update_layout(legend_title_text="Winning Supplier", margin=dict(l=10, r=10, t=55, b=10))
    st.plotly_chart(fig, width="stretch")


def render_negotiation(playbook_text, negotiation_result, assumptions=None):
    st.header("Negotiation Simulator and Playbook")
    currency, fx_rate = _display_settings(assumptions)
    c1, c2, c3 = st.columns(3)
    c1.metric("Current TCO Unit", unit_cost(negotiation_result["current_tco_unit_usd"], currency, fx_rate))
    c2.metric("Simulated TCO Unit", unit_cost(negotiation_result["simulated_tco_unit_usd"], currency, fx_rate))
    c3.metric("Annual TCO Saving", format_money(negotiation_result["annual_saving_usd"], currency, fx_rate))
    st.text_area("Generated negotiation playbook", playbook_text, height=360)
