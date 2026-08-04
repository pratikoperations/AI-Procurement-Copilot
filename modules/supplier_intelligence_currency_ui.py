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
_AUDIT_RENAME = {
    "Original Currency": "Original Quote Currency",
    "Original Unit Price": "Original Quote Unit Price",
    "Normalized Currency": "Canonical Comparison Currency",
    "Normalized Unit Price": "Canonical Comparison Unit Price",
    "FX Rate Used": "FX Rate Used (INR/USD)",
    "Unit of Measure": "Unit of Measure",
    "Comparison Basis": "Canonical Comparison Basis",
}


def _first_available(columns, candidates):
    """Return the first available canonical source column from candidates."""
    return next((column for column in candidates if column in columns), None)


def _display_column_order(frame, mode):
    """Put selected-currency business columns first for mobile visibility."""
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

    ordered = [column for column in preferred if column in frame.columns]
    ordered.extend(column for column in frame.columns if column not in ordered)
    return frame[ordered]


def _build_full_currency_frame(comparison_df, display_currency="USD", fx_rate=83):
    """Return the complete display frame before audit metadata is separated."""
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
    return _display_column_order(display, mode), mode


def build_supplier_intelligence_currency_frames(comparison_df, display_currency="USD", fx_rate=83):
    """Return separate business-facing and currency-audit frames.

    The main frame contains selected-currency business values and non-monetary
    decision fields only. Original quotation and canonical USD normalization
    metadata are preserved without mutation in a separate audit frame.
    """
    display, mode = _build_full_currency_frame(comparison_df, display_currency, fx_rate)

    audit_source_columns = ["Supplier", *_AUDIT_COLUMNS]
    available_audit = [column for column in audit_source_columns if column in display.columns]
    audit = display[available_audit].copy() if available_audit else pd.DataFrame()
    audit = audit.rename(columns=_AUDIT_RENAME)
    if not audit.empty:
        audit.insert(1 if "Supplier" in audit.columns else 0, "Display Currency", mode)

    business = display.drop(columns=_AUDIT_COLUMNS, errors="ignore")
    business = _display_column_order(business, mode)
    return business, audit


def build_supplier_intelligence_display_frame(comparison_df, display_currency="USD", fx_rate=83):
    """Return the main business-facing comparison frame only.

    Currency normalization metadata is intentionally excluded from this frame
    and is available through ``build_supplier_intelligence_currency_frames``.
    """
    business, _ = build_supplier_intelligence_currency_frames(
        comparison_df,
        display_currency=display_currency,
        fx_rate=fx_rate,
    )
    return business


def render_supplier_intelligence(intelligence, display_currency="USD", fx_rate=83):
    """Render selected-currency business values with a collapsed audit trail."""
    try:
        mode = normalize_display_currency(display_currency)
    except ValueError:
        mode = "USD"

    st.caption(
        f"Business-facing monetary columns are shown in {mode}. "
        "Canonical USD normalization is available in the collapsed audit trail."
    )

    display_intelligence = copy(intelligence or {})
    business_frame, audit_frame = build_supplier_intelligence_currency_frames(
        display_intelligence.get("comparison_df", pd.DataFrame()),
        display_currency=mode,
        fx_rate=fx_rate,
    )
    display_intelligence["comparison_df"] = business_frame
    result = _render_supplier_intelligence(display_intelligence)

    if not audit_frame.empty:
        with st.expander("Currency normalization and audit trail", expanded=False):
            st.caption(
                "Canonical comparison remains in USD for consistent ranking and traceability. "
                f"Displayed business values use {mode}; no award decision is automated."
            )
            st.dataframe(audit_frame, use_container_width=True, hide_index=True)

    return result
