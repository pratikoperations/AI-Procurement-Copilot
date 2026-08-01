"""Hosted-browser readiness overrides for Streamlit 1.59.1 mobile rendering."""

from __future__ import annotations

import streamlit as st


HOSTED_READINESS_CSS = """
/*
 * Streamlit 1.59.1 / BaseWeb select governance.
 *
 * Hosted evidence showed that the generated BaseWeb control retained two
 * independent visual states: Streamlit's primary-color treatment on the
 * immediate control shell and the application-wide focus token on a nested
 * focusable node. The nested focus indication was clipped at the trailing
 * indicator boundary and appeared as a yellow vertical stripe.
 *
 * Keep one visual owner: the immediate BaseWeb control shell. Locally remap
 * focus tokens to the governed blue, neutralize nested focus visuals, and
 * reserve red for aria-invalid only.
 */
[data-baseweb="select"] {
    --aipc-focus: var(--aipc-select-focus);
    --primary-color: var(--aipc-select-focus);
    max-width: 100% !important;
    min-width: 0 !important;
    border: 0 !important;
    outline: 3px solid transparent !important;
    outline-offset: 0 !important;
    box-shadow: none !important;
}

/* Exact visual owner for normal, focused and open select states. */
[data-baseweb="select"] > div {
    max-width: 100% !important;
    min-width: 0 !important;
    border: 1px solid var(--aipc-border) !important;
    outline: 3px solid transparent !important;
    outline-offset: 0 !important;
    box-shadow: none !important;
    transition: border-color 120ms ease, box-shadow 120ms ease;
}

/*
 * Nested BaseWeb input/combobox/tabindex nodes must not draw a second ring.
 * The transparent outline preserves the accessibility contract without using
 * outline:none. The trailing indicator shell must not expose a colored divider.
 */
[data-baseweb="select"] :is(
    input,
    [role="combobox"],
    [tabindex]:not([tabindex="-1"])
) {
    --aipc-focus: var(--aipc-select-focus);
    outline-color: transparent !important;
    box-shadow: none !important;
}

[data-baseweb="select"] :is(
    input,
    [role="combobox"],
    [tabindex]:not([tabindex="-1"])
):focus,
[data-baseweb="select"] :is(
    input,
    [role="combobox"],
    [tabindex]:not([tabindex="-1"])
):focus-visible {
    outline: 3px solid transparent !important;
    outline-offset: 0 !important;
    border-color: transparent !important;
    box-shadow: none !important;
}

[data-baseweb="select"] > div > div:last-child {
    border-left-color: transparent !important;
    outline-color: transparent !important;
    box-shadow: none !important;
}

[data-baseweb="select"]:hover > div {
    border-color: rgba(148, 163, 184, 0.65) !important;
}

[data-baseweb="select"]:focus-within > div,
[data-baseweb="select"]:has([aria-expanded="true"]) > div {
    border-color: var(--aipc-select-focus) !important;
    outline: 3px solid transparent !important;
    outline-offset: 0 !important;
    box-shadow: 0 0 0 2px rgba(88, 166, 255, 0.46) !important;
}

/* Genuine invalid state overrides valid focus/open state. */
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
