"""Currency-aware wrapper for the Supplier Intelligence Streamlit UI."""

from copy import copy

import pandas as pd
import streamlit as st

from modules.supplier_intelligence_ui import render_supplier_intelligence as _render_supplier_intelligence
from modules.utils import build_currency_display_frame, normalize_display_currency


RISK_TCO_SOURCES = (
    "Risk-Adjusted TCO USD",
    "Risk-Adjusted TCO (USD)",
    "adjusted_tco_unit_usd",
)
DISPLAY_COLUMNS = {
    "Quoted Price (USD)",
    "Quoted Price (INR)",
    "Risk-Adjusted TCO (USD)",
    "Risk-Adjusted TCO (INR)",
}
_QUOTED_PRICE_SOURCE = "__quoted_price_usd_display"
_RISK_TCO_SOURCE = "__risk_adjusted_tco_usd_display"
_AUDIT_COLUMNS = [
    "Original Currency",
    "Original Unit Price",
    "Normalized Currency",
    "Normalized Unit Price",
    "FX Rate Used",
    "Unit of Measure",
    "Comparison Basis",
]


def _first_available(columns, candidates):
    """Return the first available canonical source column from candidates."""
    return next((column for column in candidates if column in columns), None)


def _display_column_order(frame, mode):
    """Put business-facing currency columns first so they remain visible on mobile."""
    preferred = ["Supplier"]
    if mode in {"USD", "Both"}:
        preferred.extend(["Quoted Price (USD)", "Risk-Adjusted TCO (USD)"])
    if mode in {"INR", "Both"}:
        preferred.extend(["Quoted Price (INR)", "Risk-Adjusted TCO (INR)"])

    preferred.extend([
        "Risk Resilience Score",
        "Performance Score",
        "Supplier 360 Score",
        "Recommendation Status",
    ])
    preferred.extend(_AUDIT_COLUMNS)

    ordered = [column for column in preferred if column in frame.columns]
    ordered.extend(column for column in frame.columns if column not in ordered)
    return frame[ordered]


def build_supplier_intelligence_display_frame(comparison_df, display_currency="USD", fx_rate=83):
    """Return a display-only comparison frame in USD, INR, or Both.

    ``Normalized Unit Price`` remains unchanged as canonical audit metadata. A
    temporary canonical USD business column is derived from it solely to render
    Quoted Price in the selected display currency. Risk-adjusted TCO follows the
    same display-only conversion path. The supplied dataframe is never mutated.

    Business-facing currency columns are moved immediately after Supplier so the
    selected currency is visible without horizontal scrolling on mobile devices.
    Audit metadata remains present later in the same table.
    """
    original = comparison_df.copy() if isinstance(comparison_df, pd.DataFrame) else pd.DataFrame()
    try:
        mode = normalize_display_currency(display_currency)
    except ValueError:
        mode = "USD"

    risk_source = _first_available(original.columns, RISK_TCO_SOURCES)
    risk_values = original[risk_source].copy() if risk_source else None

    source = original.drop(
        columns=[column for column in DISPLAY_COLUMNS if column in original.columns],
        errors="ignore",
    )
    mapping = {}

    if "Normalized Unit Price" in source.columns:
        insert_at = source.columns.get_loc("Normalized Unit Price") + 1
        source.insert(insert_at, _QUOTED_PRICE_SOURCE, source["Normalized Unit Price"])
        mapping[_QUOTED_PRICE_SOURCE] = "Quoted Price"
    else:
        quoted_source = _first_available(source.columns, ("Quoted Price USD", "Quoted Unit Price USD"))
        if quoted_source:
            mapping[quoted_source] = "Quoted Price"

    if risk_source:
        if risk_source in source.columns:
            mapping[risk_source] = "Risk-Adjusted TCO"
        else:
            source[_RISK_TCO_SOURCE] = risk_values
            mapping[_RISK_TCO_SOURCE] = "Risk-Adjusted TCO"

    display = build_currency_display_frame(source, mapping, mode, fx_rate) if mapping else source
    return _display_column_order(display, mode)


def render_supplier_intelligence(intelligence, display_currency="USD", fx_rate=83):
    """Render Supplier Intelligence using the governed display-currency selection."""
    try:
        mode = normalize_display_currency(display_currency)
    except ValueError:
        mode = "USD"

    st.caption(
        f"Business-facing monetary columns are shown in {mode}. "
        "Original and normalized currency fields remain visible as audit metadata."
    )

    display_intelligence = copy(intelligence or {})
    display_intelligence["comparison_df"] = build_supplier_intelligence_display_frame(
        display_intelligence.get("comparison_df", pd.DataFrame()),
        display_currency=mode,
        fx_rate=fx_rate,
    )
    return _render_supplier_intelligence(display_intelligence)
