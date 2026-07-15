"""Currency-aware wrapper for the Supplier Intelligence Streamlit UI."""

from copy import copy

import pandas as pd

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


def _first_available(columns, candidates):
    """Return the first available canonical source column from candidates."""
    return next((column for column in candidates if column in columns), None)


def build_supplier_intelligence_display_frame(comparison_df, display_currency="USD", fx_rate=83):
    """Return a display-only comparison frame in USD, INR, or Both.

    ``Normalized Unit Price`` remains unchanged as canonical audit metadata. A
    temporary canonical USD business column is derived from it solely to render
    Quoted Price in the selected display currency. Risk-adjusted TCO follows the
    same display-only conversion path. The supplied dataframe is never mutated.
    """
    original = comparison_df.copy() if isinstance(comparison_df, pd.DataFrame) else pd.DataFrame()
    try:
        mode = normalize_display_currency(display_currency)
    except ValueError:
        mode = "USD"

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

    risk_source = _first_available(source.columns, RISK_TCO_SOURCES)
    if risk_source:
        mapping[risk_source] = "Risk-Adjusted TCO"

    return build_currency_display_frame(source, mapping, mode, fx_rate) if mapping else source


def render_supplier_intelligence(intelligence, display_currency="USD", fx_rate=83):
    """Render Supplier Intelligence using the governed display-currency selection."""
    display_intelligence = copy(intelligence or {})
    display_intelligence["comparison_df"] = build_supplier_intelligence_display_frame(
        display_intelligence.get("comparison_df", pd.DataFrame()),
        display_currency=display_currency,
        fx_rate=fx_rate,
    )
    return _render_supplier_intelligence(display_intelligence)
