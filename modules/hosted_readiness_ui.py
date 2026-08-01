"""Hosted-browser readiness overrides for Streamlit 1.59.1 mobile rendering."""

from __future__ import annotations

import streamlit as st


HOSTED_READINESS_CSS = """
/*
 * Theme-level interactive accent governance.
 * Streamlit Community Cloud previously rendered valid controls with its default
 * red primary color while the application-wide keyboard focus token remained
 * yellow. The combination appeared as a red select border plus a yellow stripe.
 *
 * `.streamlit/config.toml` now sets Streamlit's primary color to governed blue.
 * This final token override aligns application keyboard focus with that same
 * blue and removes the need for fragile BaseWeb select descendant selectors.
 */
:root {
    --aipc-focus: #58A6FF;
    --aipc-select-focus: #58A6FF;
    --primary-color: #58A6FF;
}

/* Preserve genuine validation red without styling normal focus as an error. */
[aria-invalid="true"] {
    border-color: var(--aipc-error) !important;
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

/* Shared containment contract. */
html,
body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    max-width: 100% !important;
    min-width: 0 !important;
}

[data-testid="stDataFrame"],
[data-testid="stTable"] {
    max-width: 100% !important;
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch;
}

/*
 * Foldable/tablet touch layout. Physical Android screenshots can expose a CSS
 * viewport wider than a conventional phone even though the available content
 * width is narrow after the sidebar opens. Use pointer capability plus a broad
 * width ceiling to force critical Streamlit columns into a readable two-column
 * grid. Conventional desktop pointers keep the desktop multi-column layout.
 */
@media (hover: none) and (pointer: coarse) and (max-width: 1400px) {
    html,
    body,
    [data-testid="stApp"],
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    [data-testid="stMainBlockContainer"] {
        width: 100% !important;
        overflow-x: clip !important;
    }

    [data-testid="stHorizontalBlock"] {
        display: grid !important;
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;
        gap: 0.75rem !important;
    }

    [data-testid="stHorizontalBlock"] > [data-testid="column"],
    [data-testid="stHorizontalBlock"] > .stColumn,
    div[data-testid="column"],
    .stColumn {
        flex: none !important;
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

    [data-testid="stSidebar"] {
        max-width: min(22rem, 92vw) !important;
    }

    [data-testid="stSidebarContent"] {
        max-width: 100% !important;
        overflow-x: clip !important;
    }
}

/* Narrow touch screens use one column. */
@media (hover: none) and (pointer: coarse) and (max-width: 760px),
       (max-width: 600px) {
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: column !important;
        flex-wrap: nowrap !important;
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;
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
}
"""


def apply_hosted_readiness_overrides() -> None:
    """Apply browser-specific presentation overrides without changing logic."""
    st.markdown(f"<style>{HOSTED_READINESS_CSS}</style>", unsafe_allow_html=True)
