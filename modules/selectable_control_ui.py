"""Presentation-only styling for globally discoverable Streamlit selectbox controls."""
from __future__ import annotations

import streamlit as st

SELECTABLE_CONTROL_CSS = """
<style>
/* Streamlit 1.59+ React Aria selectbox surface. */
[data-testid="stSelectbox"] .react-aria-ComboBox > [role="group"]:not(:has(input:disabled)):not(:has(input[aria-disabled="true"])) {
    background: rgba(47, 128, 237, 0.08) !important;
    border-color: rgba(88, 166, 255, 0.42) !important;
    box-shadow: none !important;
    transition: background-color 120ms ease, border-color 120ms ease, box-shadow 120ms ease;
}

[data-testid="stSelectbox"] .react-aria-ComboBox > [role="group"]:not(:has(input:disabled)):not(:has(input[aria-disabled="true"])):hover {
    background: rgba(47, 128, 237, 0.14) !important;
    border-color: rgba(88, 166, 255, 0.72) !important;
}

[data-testid="stSelectbox"] .react-aria-ComboBox > [role="group"]:not(:has(input:disabled)):not(:has(input[aria-disabled="true"])):focus-within {
    background: rgba(47, 128, 237, 0.12) !important;
    border-color: #58A6FF !important;
    box-shadow: 0 0 0 2px rgba(88, 166, 255, 0.35) !important;
}

[data-testid="stSelectbox"] .react-aria-ComboBox input[role="combobox"]:focus-visible {
    outline: 3px solid transparent !important;
    outline-offset: 0 !important;
    box-shadow: none !important;
}

[data-testid="stSelectbox"] .react-aria-ComboBox > [role="group"]:has(input[aria-invalid="true"]) {
    background: rgba(197, 48, 48, 0.08) !important;
    border-color: #C53030 !important;
    box-shadow: 0 0 0 2px rgba(197, 48, 48, 0.28) !important;
}

/* Compatibility fallback for older Streamlit/BaseWeb selectbox markup. */
[data-testid="stSelectbox"] [data-baseweb="select"]:not(:has([aria-disabled="true"])) > div {
    background: rgba(47, 128, 237, 0.08) !important;
    border-color: rgba(88, 166, 255, 0.42) !important;
    box-shadow: none !important;
    transition: background-color 120ms ease, border-color 120ms ease, box-shadow 120ms ease;
}

[data-testid="stSelectbox"] [data-baseweb="select"]:not(:has([aria-disabled="true"])):hover > div {
    background: rgba(47, 128, 237, 0.14) !important;
    border-color: rgba(88, 166, 255, 0.72) !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"]:not(:has([aria-disabled="true"])):focus-within > div {
    background: rgba(47, 128, 237, 0.12) !important;
    border-color: #58A6FF !important;
    box-shadow: 0 0 0 2px rgba(88, 166, 255, 0.35) !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"] [role="combobox"]:focus-visible {
    outline: 3px solid transparent !important;
    outline-offset: 0 !important;
    box-shadow: none !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"]:has([aria-invalid="true"]) > div {
    background: rgba(197, 48, 48, 0.08) !important;
    border-color: #C53030 !important;
    box-shadow: 0 0 0 2px rgba(197, 48, 48, 0.28) !important;
}
</style>
"""


def render_selectable_control_distinction() -> None:
    """Inject selectbox-only visual distinction without changing widget behavior."""
    st.markdown(SELECTABLE_CONTROL_CSS, unsafe_allow_html=True)
