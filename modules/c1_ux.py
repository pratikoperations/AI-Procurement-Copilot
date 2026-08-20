"""Presentation-only helpers for the controlled C1 Kraft Paper UX."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from modules.sourcemate_application_shell import mount_global_sourcemate


CATEGORY_INTELLIGENCE_METRIC_CSS = """
/* Keep long category labels readable inside Selected Category Intelligence. */
[data-testid="stExpander"] [data-testid="stMetricValue"] > div {
    font-size: clamp(1rem, 2.2vw, 1.5rem) !important;
    overflow-wrap: normal !important;
    word-break: normal !important;
}
"""


def apply_c1_ux_overrides() -> None:
    """Apply scoped presentation overrides and the shared project assistant shell."""
    mount_global_sourcemate("AI Procurement Copilot")
    st.markdown(f"<style>{CATEGORY_INTELLIGENCE_METRIC_CSS}</style>", unsafe_allow_html=True)


def technical_eligibility_label(value) -> str:
    """Return an executive-readable technical-eligibility label."""
    if pd.isna(value):
        return "Not assessed"
    return "Eligible" if bool(value) else "Ineligible"
