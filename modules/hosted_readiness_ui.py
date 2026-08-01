"""Hosted-browser readiness overrides for Streamlit 1.59.1 mobile rendering."""

from __future__ import annotations

import streamlit as st


HOSTED_READINESS_CSS = """
/*
 * Streamlit 1.59.1 / BaseWeb select governance.
 * Target both the select wrapper and the actual combobox element because the
 * generated DOM can place focus, border and aria-expanded state on different
 * nested nodes across desktop and mobile browsers.
 */
[data-baseweb="select"],
[data-baseweb="select"] > div,
[data-baseweb="select"] [role="combobox"] {
    max-width: 100% !important;
    min-width: 0 !important;
}

[data-baseweb="select"] > div,
[data-baseweb="select"] [role="combobox"] {
    border-color: var(--aipc-border) !important;
    outline: 3px solid transparent !important;
    outline-offset: 0 !important;
    box-shadow: none !important;
}

[data-baseweb="select"]:hover > div,
[data-baseweb="select"] [role="combobox"]:hover {
    border-color: rgba(148, 163, 184, 0.65) !important;
}

[data-baseweb="select"]:focus-within > div,
[data-baseweb="select"]:focus-within [role="combobox"],
[data-baseweb="select"] [role="combobox"]:focus,
[data-baseweb="select"] [role="combobox"]:focus-visible,
[data-baseweb="select"] [role="combobox"][aria-expanded="true"] {
    border-color: var(--aipc-select-focus) !important;
    outline: 3px solid transparent !important;
    outline-offset: 0 !important;
    box-shadow: 0 0 0 2px rgba(88, 166, 255, 0.42) !important;
}

[data-baseweb="select"]:has([aria-invalid="true"]) > div,
[data-baseweb="select"] [role="combobox"][aria-invalid="true"] {
    border-color: var(--aipc-error) !important;
    box-shadow: 0 0 0 2px rgba(197, 48, 48, 0.32) !important;
}

/* Keep menu options readable and selected state unambiguous. */
[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"] {
    max-width: min(92vw, 34rem) !important;
}

[role="option"] {
    white-space: normal !important;
    overflow-wrap: anywhere !important;
}

/*
 * Mobile cards: Streamlit may retain inline column widths. Force a vertical
 * flow at narrow browser widths, including .stColumn wrappers used by recent
 * Streamlit releases.
 */
@media (max-width: 900px) {
    html,
    body,
    [data-testid="stApp"],
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] {
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;
        overflow-x: clip !important;
    }

    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: column !important;
        flex-wrap: nowrap !important;
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;
        gap: 0.75rem !important;
    }

    [data-testid="stHorizontalBlock"] > [data-testid="column"],
    [data-testid="stHorizontalBlock"] > .stColumn,
    div[data-testid="column"],
    .stColumn {
        flex: 1 1 100% !important;
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;
    }

    [data-testid="stMetric"] {
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;
        height: auto !important;
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"],
    [data-testid="stMetricDelta"],
    [data-testid="stMetricLabel"] *,
    [data-testid="stMetricValue"] *,
    [data-testid="stMetricDelta"] * {
        word-break: normal !important;
        overflow-wrap: break-word !important;
        white-space: normal !important;
    }

    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        max-width: 100% !important;
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch;
    }

    [data-testid="stSidebar"] {
        max-width: min(22rem, 92vw) !important;
    }

    [data-testid="stSidebarContent"] {
        max-width: 100% !important;
        overflow-x: clip !important;
    }
}
"""


def apply_hosted_readiness_overrides() -> None:
    """Apply browser-specific presentation overrides without changing logic."""
    st.markdown(f"<style>{HOSTED_READINESS_CSS}</style>", unsafe_allow_html=True)
