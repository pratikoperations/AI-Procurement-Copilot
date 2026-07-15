"""Currency-aware wrapper for the Supplier Intelligence Streamlit UI."""

from copy import copy

import pandas as pd

from modules.supplier_intelligence_ui import render_supplier_intelligence as _render_supplier_intelligence
from modules.utils import build_currency_display_frame, normalize_display_currency


CURRENCY_COLUMNS = {
    "Quoted Price USD": "Quoted Price",
    "Risk-Adjusted TCO USD": "Risk-Adjusted TCO",
    "Risk-Adjusted TCO (USD)": "Risk-Adjusted TCO",
    "adjusted_tco_unit_usd": "Risk-Adjusted TCO",
}
DISPLAY_COLUMNS = {
    "Quoted Price (USD)",
    "Quoted Price (INR)",
    "Risk-Adjusted TCO (USD)",
    "Risk-Adjusted TCO (INR)",
}


def _currency_mapping(columns):
    """Select at most one canonical source column for each business label."""
    selected = {}
    used_labels = set()
    for column, label in CURRENCY_COLUMNS.items():
        if column in columns and label not in used_labels:
            selected[column] = label
            used_labels.add(label)
    return selected


def build_supplier_intelligence_display_frame(comparison_df, display_currency="USD", fx_rate=83):
    """Return a display-only comparison frame in USD, INR, or Both.

    Source and audit metadata columns are preserved. Canonical USD business fields
    are converted only for display and the supplied dataframe is never mutated.
    Invalid display modes fall back to USD for backward-compatible rendering.
    """
    original = comparison_df.copy() if isinstance(comparison_df, pd.DataFrame) else pd.DataFrame()
    try:
        mode = normalize_display_currency(display_currency)
    except ValueError:
        mode = "USD"

    mapping = _currency_mapping(original.columns)
    if not mapping:
        return original

    source = original.drop(
        columns=[column for column in DISPLAY_COLUMNS if column in original.columns and column not in mapping],
        errors="ignore",
    )
    return build_currency_display_frame(source, mapping, mode, fx_rate)


def render_supplier_intelligence(intelligence, display_currency="USD", fx_rate=83):
    """Render Supplier Intelligence using the governed display-currency selection."""
    display_intelligence = copy(intelligence or {})
    display_intelligence["comparison_df"] = build_supplier_intelligence_display_frame(
        display_intelligence.get("comparison_df", pd.DataFrame()),
        display_currency=display_currency,
        fx_rate=fx_rate,
    )
    return _render_supplier_intelligence(display_intelligence)
