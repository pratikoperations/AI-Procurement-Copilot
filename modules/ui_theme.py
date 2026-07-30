"""Presentation-only design tokens and Streamlit UI hardening for Build S1.1."""

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
    --aipc-info: #2F80ED;
    --aipc-success: #2E8B57;
    --aipc-warning: #B7791F;
    --aipc-error: #C53030;
}

/* Main-page rhythm and readable content width. */
[data-testid="stMainBlockContainer"] {
    max-width: 1440px;
    padding-top: 1.75rem;
    padding-bottom: 3rem;
}

[data-testid="stMainBlockContainer"] h1 {
    line-height: 1.12;
    letter-spacing: -0.025em;
    margin-bottom: var(--aipc-space-3);
}

[data-testid="stMainBlockContainer"] h2,
[data-testid="stMainBlockContainer"] h3 {
    line-height: 1.22;
    letter-spacing: -0.012em;
    margin-top: var(--aipc-space-6);
    margin-bottom: var(--aipc-space-3);
}

[data-testid="stHorizontalBlock"] {
    gap: var(--aipc-space-4);
    align-items: stretch;
}

/* Consistent card treatment for metrics and status surfaces. */
[data-testid="stMetric"] {
    height: 100%;
    padding: var(--aipc-space-4);
    border: 1px solid var(--aipc-border);
    border-radius: var(--aipc-radius-md);
    background: var(--aipc-surface);
}

[data-testid="stAlert"] {
    border-radius: var(--aipc-radius-md);
    padding-top: var(--aipc-space-3);
    padding-bottom: var(--aipc-space-3);
}

[data-testid="stExpander"] {
    border-radius: var(--aipc-radius-md);
    overflow: hidden;
}

[data-testid="stDataFrame"],
[data-testid="stTable"] {
    border: 1px solid var(--aipc-border);
    border-radius: var(--aipc-radius-md);
    overflow: hidden;
}

/* Sidebar consistency and touch-safe controls. */
[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    padding-top: var(--aipc-space-4);
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
    min-height: 2.75rem;
    border-radius: var(--aipc-radius-sm);
    font-weight: 600;
}

[data-baseweb="select"] > div,
[data-baseweb="input"] > div,
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input {
    border-radius: var(--aipc-radius-sm);
}

/* Preserve usable spacing on narrow screens without changing navigation. */
@media (max-width: 768px) {
    [data-testid="stMainBlockContainer"] {
        padding: 1rem 0.85rem 2rem;
    }

    [data-testid="stHorizontalBlock"] {
        gap: var(--aipc-space-3);
    }

    [data-testid="stMetric"] {
        padding: var(--aipc-space-3);
    }
}
"""


def apply_ui_theme() -> None:
    """Apply the S1.1 presentation layer without changing application data or logic."""
    st.markdown(f"<style>{UI_CSS}</style>", unsafe_allow_html=True)
