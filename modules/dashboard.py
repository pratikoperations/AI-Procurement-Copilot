"""Dashboard rendering functions."""

import streamlit as st
import plotly.express as px


def render_executive_dashboard(suppliers_df, assumptions):
    """Render Build 0.2 executive dashboard shell."""
    st.subheader("Executive Dashboard")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Category Engine", assumptions["category"])
    c2.metric("Annual Volume", f"{assumptions['annual_volume']:,.0f}")
    c3.metric("Supplier Count", len(suppliers_df))
    c4.metric("Build", "0.2")

    st.caption(
        "Build 0.2 establishes the Streamlit framework and modular skeleton. Full procurement scoring engines start in Build 0.3."
    )


def render_supplier_snapshot(suppliers_df):
    """Render starter supplier table and simple quote chart."""
    st.header("Supplier RFQ Snapshot")
    st.dataframe(suppliers_df, use_container_width=True, hide_index=True)

    if "Quoted Unit Price USD" in suppliers_df.columns and "Supplier" in suppliers_df.columns:
        fig = px.bar(
            suppliers_df,
            x="Supplier",
            y="Quoted Unit Price USD",
            title="Quoted Unit Price by Supplier",
            text_auto=".4f",
        )
        st.plotly_chart(fig, use_container_width=True)
