"""Currency and unit normalization for auditable supplier comparison."""

from __future__ import annotations

import pandas as pd

SUPPORTED_TO_USD = {"USD", "INR"}


def normalize_comparison_basis(df: pd.DataFrame, fx_rate: float | None, base_currency: str = "USD"):
    """Preserve original quotation data and normalize supported currencies to USD.

    `fx_rate` is interpreted as INR per USD. Unsupported currencies are preserved
    and reported as blockers rather than silently converted.
    """
    result = df.copy()
    if "Currency" not in result.columns:
        result["Currency"] = base_currency
    if "Unit" not in result.columns:
        result["Unit"] = "piece"

    result["Original Currency"] = result["Currency"].fillna("").astype(str).str.upper().str.strip()
    result["Original Unit Price"] = pd.to_numeric(result["Quoted Unit Price USD"], errors="coerce")
    result["Unit of Measure"] = result["Unit"].fillna("").astype(str).str.strip()
    result["Normalized Currency"] = base_currency
    result["FX Rate Used"] = 1.0
    result["Comparison Basis"] = result["Normalized Currency"] + " per " + result["Unit of Measure"]

    blockers = []
    normalized_prices = []
    normalized_currency_values = []
    normalized_fx = []

    for _, row in result.iterrows():
        currency = str(row["Original Currency"] or base_currency).upper()
        price = row["Original Unit Price"]
        if currency == base_currency:
            normalized_prices.append(price)
            normalized_currency_values.append(base_currency)
            normalized_fx.append(1.0)
        elif currency == "INR" and base_currency == "USD" and fx_rate and float(fx_rate) > 0:
            normalized_prices.append(float(price) / float(fx_rate))
            normalized_currency_values.append(base_currency)
            normalized_fx.append(float(fx_rate))
        else:
            normalized_prices.append(price)
            normalized_currency_values.append(currency)
            normalized_fx.append(None)
            blockers.append(f"No approved FX conversion is available from {currency} to {base_currency}.")

    result["Normalized Unit Price"] = normalized_prices
    result["Normalized Currency"] = normalized_currency_values
    result["FX Rate Used"] = normalized_fx
    result["Quoted Unit Price USD"] = result["Normalized Unit Price"]
    result["Currency"] = result["Normalized Currency"]
    result.attrs.update(df.attrs)
    result.attrs["currency_unit_governance"] = {
        "base_currency": base_currency,
        "blockers": sorted(set(blockers)),
        "normalized": not blockers,
    }
    return result


def validate_category_unit(df: pd.DataFrame, category: str, commodity: str) -> list[str]:
    """Return category-specific unit warnings."""
    units = set(df.get("Unit", pd.Series(dtype=str)).dropna().astype(str).str.lower())
    warnings = []
    if category == "Raw Material Procurement" and commodity == "PET Resin" and units != {"kg"}:
        warnings.append("PET Resin quotations must use kg as the comparison unit.")
    return warnings
