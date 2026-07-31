"""Currency and unit normalization for auditable supplier comparison."""

from __future__ import annotations

import pandas as pd


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
    price_source = "Quoted Unit Price USD"
    if "Quoted Unit Price" in result.columns and (
        price_source not in result.columns or result[price_source].isna().any()
    ):
        raw_price = pd.to_numeric(result["Quoted Unit Price"], errors="coerce")
        if price_source not in result.columns:
            result[price_source] = raw_price
        else:
            result[price_source] = pd.to_numeric(result[price_source], errors="coerce").fillna(raw_price)
    result["Original Unit Price"] = pd.to_numeric(result[price_source], errors="coerce")
    result["Unit of Measure"] = result["Unit"].fillna("").astype(str).str.strip()

    blockers = []
    normalized_prices = []
    normalized_currency_values = []
    normalized_fx = []

    for _, row in result.iterrows():
        currency = str(row["Original Currency"] or base_currency).upper()
        price = row["Original Unit Price"]
        if pd.isna(price):
            normalized_prices.append(price)
            normalized_currency_values.append(currency)
            normalized_fx.append(None)
            blockers.append("A supplier quotation is missing a numeric unit price.")
        elif currency == base_currency:
            normalized_prices.append(float(price))
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
    result["Comparison Basis"] = result["Normalized Currency"] + " per " + result["Unit of Measure"]
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
    """Attach selected category context and return category-specific unit warnings."""
    df.attrs["category"] = category
    df.attrs["commodity"] = commodity

    units = set(df.get("Unit", pd.Series(dtype=str)).dropna().astype(str).str.lower())
    warnings = []
    if category == "Raw Material Procurement" and commodity in {"PET Resin", "Kraft Paper", "Steel"} and units != {"kg"}:
        warnings.append(f"{commodity} quotations must use kg as the comparison unit.")
    return warnings
