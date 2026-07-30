"""Presentation-only design tokens and Streamlit UI hardening for Build S1.1/S1.3/S1.5/S1.5.1."""

from __future__ import annotations

import streamlit as st


STATUS_COLORS = {
    "info": "#2F80ED",
    "success": "#2E8B57",
    "warning": "#B7791F",
    "error": "#C53030",
}

UI_CSS = """
:root {
    --aipc-space-1: 0.25rem;
    --aipc-space-2: 0.5rem;
    --aipc-space-3: 0.75rem;
    --aipc-space-4: 1rem;
    --aipc-space-6: 1.5rem;
    --aipc-radius-sm: 0.5rem;
    --aipc-radius-md: 0.75rem;
    --aipc-border: rgba(128, 128, 128, 0.28);
    --aipc-surface: rgba(128, 128, 128, 0.06);
    --aipc-focus: #F2C94C;
    --aipc-info: #2F80ED;
    --aipc-success: #2E8B57;
    --aipc-warning: #B7791F;
    --aipc-error: #C53030;
}

/* Prevent generated Streamlit wrappers from creating viewport-level overflow. */
html,
body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    max-width: 100%;
    min-width: 0;
}

html,
body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    overflow-x: clip;
}

*,
*::before,
*::after {
    box-sizing: border-box;
}

/* Main-page rhythm and readable content width. */
[data-testid="stMainBlockContainer"] {
    width: min(100%, 1440px);
    padding-top: 1.75rem;
    padding-bottom: 3rem;
    overflow-x: clip;
}

[data-testid="stMainBlockContainer"] > div,
[data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"],
[data-testid="stMainBlockContainer"] [data-testid="stElementContainer"] {
    max-width: 100%;
    min-width: 0;
}

[data-testid="stMainBlockContainer"] h1 {
    max-width: 100%;
    line-height: 1.12;
    letter-spacing: -0.025em;
    margin-bottom: var(--aipc-space-3);
    overflow-wrap: anywhere;
}

[data-testid="stMainBlockContainer"] h2,
[data-testid="stMainBlockContainer"] h3 {
    max-width: 100%;
    line-height: 1.22;
    letter-spacing: -0.012em;
    margin-top: var(--aipc-space-6);
    margin-bottom: var(--aipc-space-3);
    overflow-wrap: anywhere;
}

[data-testid="stHorizontalBlock"] {
    width: 100%;
    max-width: 100%;
    gap: var(--aipc-space-4);
    align-items: stretch;
    min-width: 0;
}

[data-testid="stHorizontalBlock"] > [data-testid="column"] {
    max-width: 100%;
    min-width: 0;
}

/* Visible keyboard focus without suppressing native semantics. */
:where(
    button,
    a,
    input,
    textarea,
    [role="button"],
    [role="radio"],
    [role="checkbox"],
    [role="combobox"],
    [tabindex]:not([tabindex="-1"])
):focus-visible {
    outline: 3px solid var(--aipc-focus) !important;
    outline-offset: 3px !important;
    box-shadow: 0 0 0 2px rgba(15, 23, 42, 0.85) !important;
}

/* Consistent card treatment for metrics and status surfaces. */
[data-testid="stMetric"] {
    width: 100%;
    max-width: 100%;
    height: 100%;
    min-width: 0;
    padding: var(--aipc-space-4);
    border: 1px solid var(--aipc-border);
    border-radius: var(--aipc-radius-md);
    background: var(--aipc-surface);
    overflow: hidden;
}

[data-testid="stMetricLabel"],
[data-testid="stMetricValue"],
[data-testid="stMetricDelta"],
[data-testid="stMetricLabel"] *,
[data-testid="stMetricValue"] *,
[data-testid="stMetricDelta"] * {
    max-width: 100% !important;
    min-width: 0 !important;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
    overflow-wrap: anywhere !important;
    word-break: break-word !important;
}

[data-testid="stMetricLabel"] > div,
[data-testid="stMetricValue"] > div,
[data-testid="stMetricDelta"] > div {
    display: block !important;
    width: 100% !important;
    line-height: 1.15;
}

[data-testid="stAlert"] {
    max-width: 100%;
    min-width: 0;
    border-radius: var(--aipc-radius-md);
    padding-top: var(--aipc-space-3);
    padding-bottom: var(--aipc-space-3);
    overflow-wrap: anywhere;
}

[data-testid="stAlert"] p,
[data-testid="stAlert"] div {
    white-space: normal;
    overflow-wrap: anywhere;
}

[data-testid="stExpander"] {
    max-width: 100%;
    min-width: 0;
    border-radius: var(--aipc-radius-md);
    overflow: hidden;
}

[data-testid="stExpanderDetails"] {
    max-width: 100%;
    min-width: 0;
    overflow-x: clip;
}

[data-testid="stDataFrame"],
[data-testid="stTable"] {
    width: 100%;
    max-width: 100%;
    min-width: 0;
    border: 1px solid var(--aipc-border);
    border-radius: var(--aipc-radius-md);
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}

/* Keep upload controls and file metadata within the available viewport. */
[data-testid="stFileUploader"],
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploaderFile"] {
    max-width: 100%;
    min-width: 0;
}

[data-testid="stFileUploaderFileName"] {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* Sidebar consistency and touch-safe controls. */
[data-testid="stSidebar"] {
    max-width: min(21rem, 88vw);
}

[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    max-width: 100%;
    padding-top: var(--aipc-space-4);
    overflow-x: clip;
}

[data-testid="stSidebar"] h1 {
    font-size: 1.45rem;
    line-height: 1.2;
    margin-bottom: var(--aipc-space-2);
}

[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    margin-top: var(--aipc-space-4);
    margin-bottom: var(--aipc-space-2);
}

[data-testid="stSidebar"] hr {
    margin: var(--aipc-space-6) 0;
}

.stButton > button,
.stDownloadButton > button {
    max-width: 100%;
    min-height: 2.75rem;
    border-radius: var(--aipc-radius-sm);
    font-weight: 600;
    white-space: normal;
}

[data-baseweb="select"] > div,
[data-baseweb="input"] > div,
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input {
    max-width: 100%;
    min-height: 2.75rem;
    border-radius: var(--aipc-radius-sm);
}

/* Tablet layout: use two-column cards and prevent intrinsic-width overflow. */
@media (max-width: 1024px) {
    [data-testid="stMainBlockContainer"] {
        width: 100%;
        max-width: 100%;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    [data-testid="stHorizontalBlock"] {
        width: 100%;
        max-width: 100%;
        min-width: 0;
        flex-wrap: wrap !important;
    }

    [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        flex: 1 1 calc(50% - var(--aipc-space-4)) !important;
        width: calc(50% - var(--aipc-space-4)) !important;
        max-width: 100% !important;
        min-width: min(15rem, 100%) !important;
    }

    [data-testid="stMetric"] {
        width: 100%;
        max-width: 100%;
    }

    [data-testid="stMetricValue"] > div {
        font-size: clamp(1.4rem, 4.5vw, 2.15rem) !important;
    }
}

/* Mobile layout: stack columns and keep all content inside the viewport. */
@media (max-width: 768px) {
    [data-testid="stMainBlockContainer"] {
        width: 100%;
        max-width: 100%;
        padding: 1rem 0.85rem 2rem;
    }

    [data-testid="stMainBlockContainer"] h1 {
        font-size: clamp(2rem, 9vw, 3rem);
    }

    [data-testid="stHorizontalBlock"] {
        gap: var(--aipc-space-3);
        flex-wrap: wrap !important;
    }

    [data-testid="stHorizontalBlock"] > [data-testid="column"] {
        flex: 1 1 100% !important;
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;
    }

    [data-testid="stMetric"] {
        padding: var(--aipc-space-3);
    }

    [data-testid="stMetricValue"] > div {
        font-size: clamp(1.35rem, 7vw, 2rem) !important;
    }

    [data-testid="stExpanderDetails"] {
        padding-left: var(--aipc-space-3);
        padding-right: var(--aipc-space-3);
    }

    [data-testid="stFileUploaderDropzone"] {
        padding-left: var(--aipc-space-3);
        padding-right: var(--aipc-space-3);
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


def apply_ui_theme() -> None:
    """Apply the presentation layer without changing application data or logic."""
    st.markdown(f"<style>{UI_CSS}</style>", unsafe_allow_html=True)
