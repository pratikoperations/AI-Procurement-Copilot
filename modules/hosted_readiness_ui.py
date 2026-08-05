"""Hosted-browser readiness overrides for Streamlit 1.59.1 mobile rendering."""

from __future__ import annotations

import streamlit as st


HOSTED_READINESS_CSS = """
:root {
    --aipc-focus: #58A6FF;
    --aipc-select-focus: #58A6FF;
    --primary-color: #58A6FF;
    --aipc-safe-top: env(safe-area-inset-top, 0px);
    --aipc-safe-right: env(safe-area-inset-right, 0px);
    --aipc-safe-bottom: env(safe-area-inset-bottom, 0px);
    --aipc-safe-left: env(safe-area-inset-left, 0px);
}

[aria-invalid="true"] {
    border-color: var(--aipc-error) !important;
}

[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"] {
    max-width: min(92vw, 34rem) !important;
}

[role="option"] {
    white-space: normal !important;
    overflow-wrap: anywhere !important;
}

html,
body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    max-width: 100% !important;
    min-width: 0 !important;
}

[data-testid="stAppViewContainer"] {
    min-height: 100vh;
    min-height: 100dvh;
}

[data-testid="stDataFrame"],
[data-testid="stTable"] {
    max-width: 100% !important;
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch;
    overscroll-behavior-inline: contain;
}

/* Mobile controls must remain reliably touch-operable. */
@media (hover: none) and (pointer: coarse) {
    button,
    [role="button"],
    input,
    textarea,
    select,
    [data-baseweb="select"] {
        min-height: 44px !important;
    }

    [data-testid="stMainBlockContainer"] {
        padding-left: max(1rem, var(--aipc-safe-left)) !important;
        padding-right: max(1rem, var(--aipc-safe-right)) !important;
        padding-bottom: max(5.5rem, calc(1rem + var(--aipc-safe-bottom))) !important;
    }
}

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
        padding-top: var(--aipc-safe-top) !important;
        padding-left: var(--aipc-safe-left) !important;
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

    h1 { font-size: clamp(1.65rem, 8vw, 2.2rem) !important; }
    h2 { font-size: clamp(1.35rem, 6.5vw, 1.8rem) !important; }
    h3 { font-size: clamp(1.15rem, 5.5vw, 1.5rem) !important; }
}

/*
 * Folded-phone desktop-site mode commonly exposes a CSS viewport near 980px.
 * Preserve the desktop-style two-column presentation so the enlarged CSS
 * viewport is fully used. Only the sidebar width and collapsed-state recovery
 * are specialized for this device mode.
 */
@media (hover: none) and (pointer: coarse) and (min-width: 900px) and (max-width: 1000px) {
    [data-testid="stSidebar"] {
        width: min(18rem, 36vw) !important;
        max-width: min(18rem, 36vw) !important;
    }

    [data-testid="stSidebarContent"] {
        padding-right: 0.75rem !important;
    }

    [data-testid="stMainBlockContainer"] {
        padding-left: max(0.75rem, var(--aipc-safe-left)) !important;
        padding-right: max(0.75rem, var(--aipc-safe-right)) !important;
    }

    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        min-height: 12rem;
    }

    /*
     * Streamlit keeps the sidebar element mounted after collapse. The forced
     * Fold-width above must be removed when the element contains the native
     * Open-sidebar control, otherwise a blank column remains reserved.
     */
    [data-testid="stSidebar"]:has(button[aria-label="Open sidebar"]) {
        flex: 0 0 0 !important;
        width: 0 !important;
        min-width: 0 !important;
        max-width: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: visible !important;
    }

    [data-testid="stSidebar"]:has(button[aria-label="Open sidebar"])
    [data-testid="stSidebarContent"] {
        display: none !important;
    }
}

@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        scroll-behavior: auto !important;
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
"""


def apply_hosted_readiness_overrides() -> None:
    """Apply browser-specific presentation overrides without changing logic."""
    st.markdown(f"<style>{HOSTED_READINESS_CSS}</style>", unsafe_allow_html=True)
