"""Sidebar controls for the Streamlit app."""

import streamlit as st

from modules.category_engine import ensure_category_profile, get_category_profile
from modules.config import DEFAULT_FX_RATE, FUTURE_CATEGORIES, SUPPORTED_CATEGORIES


def build_sidebar_result(**values):
    """Build the governed sidebar return contract with a guaranteed category profile."""
    result = dict(values)
    result["category_profile"] = ensure_category_profile(result.get("category_profile"))
    return result


def render_sidebar():
    """Render sidebar controls and always return a complete assumptions dictionary."""
    st.sidebar.title("AI Procurement Copilot")
    st.sidebar.caption("Portfolio Edition v1.0")

    data_source = st.sidebar.radio(
        "Data Source",
        ["Synthetic Demo", "Upload RFQ CSV/Excel"],
        index=0,
    )

    category = st.sidebar.selectbox(
        "Category Engine",
        SUPPORTED_CATEGORIES,
        index=0,
    )

    base_profile = ensure_category_profile(get_category_profile(category))
    commodity = st.sidebar.selectbox(
        "Commodity / Material",
        base_profile["commodities"],
        index=0,
    )
    category_profile = ensure_category_profile(get_category_profile(category, commodity))

    if category_profile["engine_status"] != "Active":
        st.sidebar.warning(
            "Raw-material architecture is available as a foundation preview. "
            "Full category-specific scoring is planned for Build 0.9.4."
        )

    with st.sidebar.expander("Future Category Engines"):
        for item in FUTURE_CATEGORIES:
            st.write(f"Planned: {item}")

    st.sidebar.markdown("---")
    st.sidebar.subheader("Currency")
    fx_rate = st.sidebar.slider("USD-INR FX Rate", 75, 95, DEFAULT_FX_RATE)
    display_currency = st.sidebar.radio("Display Currency", ["USD", "INR", "Both"], index=2)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Scenario Assumptions")
    annual_volume = st.sidebar.number_input("Annual Volume", min_value=1000, value=500000, step=10000)
    raw_material_shock = st.sidebar.slider("Raw Material Shock %", -20, 40, 0) / 100
    freight_shock = st.sidebar.slider("Freight Shock %", -20, 80, 0) / 100
    demand_change = st.sidebar.slider("Demand Change %", -50, 50, 0) / 100

    st.sidebar.markdown("---")
    st.sidebar.subheader("Allocation Constraints")
    max_supplier_share = st.sidebar.slider("Max Supplier Share %", 50, 100, 75)
    min_backup_share = st.sidebar.slider("Minimum Backup Share %", 0, 40, 25)
    min_risk_score = st.sidebar.slider("Minimum Risk Score", 0, 100, 55)
    min_esg_score = st.sidebar.slider("Minimum ESG Score", 0, 100, 50)

    return build_sidebar_result(
        data_source=data_source,
        category=category,
        commodity=commodity,
        category_profile=category_profile,
        fx_rate=fx_rate,
        display_currency=display_currency,
        annual_volume=annual_volume,
        raw_material_shock=raw_material_shock,
        freight_shock=freight_shock,
        demand_change=demand_change,
        max_supplier_share=max_supplier_share,
        min_backup_share=min_backup_share,
        min_risk_score=min_risk_score,
        min_esg_score=min_esg_score,
    )
