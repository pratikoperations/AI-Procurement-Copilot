"""Shared utility functions."""

import re


def extract_number(value, default=0.0):
    """Extract the first numeric value from text such as '10,000' or '30 Days'."""
    if isinstance(value, (int, float)):
        return float(value)
    match = re.search(r"[\d,.]+", str(value))
    return float(match.group(0).replace(",", "")) if match else float(default)


def safe_positive(value, floor=1.0):
    """Return a positive numeric value with a floor to avoid divide-by-zero issues."""
    return max(float(value), float(floor))


def normalize_score(value):
    """Clamp a numeric score between 0 and 100."""
    return max(min(float(value), 100.0), 0.0)


def normalize_display_currency(currency):
    """Return one of the governed display modes: USD, INR, or Both."""
    value = str(currency or "USD").strip().upper()
    if value == "BOTH":
        return "Both"
    if value in {"USD", "INR"}:
        return value
    raise ValueError(f"Unsupported display currency: {currency}")


def currency_label(currency):
    """Return a readable label for a display-currency mode."""
    mode = normalize_display_currency(currency)
    return "USD / INR" if mode == "Both" else mode


def convert_from_usd(value, currency="USD", fx_rate=83):
    """Convert a canonical USD value for display without mutating source data."""
    mode = normalize_display_currency(currency)
    amount = float(value)
    if mode == "INR":
        return amount * float(fx_rate)
    return amount


def format_money(value, currency="USD", fx_rate=83, decimals=0):
    """Format a canonical USD amount in USD, INR, or both currencies."""
    mode = normalize_display_currency(currency)
    amount = float(value)
    if mode == "USD":
        return f"${amount:,.{decimals}f}"
    if mode == "INR":
        return f"₹{amount * float(fx_rate):,.{decimals}f}"
    return f"${amount:,.{decimals}f} / ₹{amount * float(fx_rate):,.{decimals}f}"


def money_usd(value):
    """Backward-compatible USD formatter."""
    return format_money(value, "USD", decimals=0)


def money_inr(value, fx_rate):
    """Backward-compatible INR formatter for canonical USD values."""
    return format_money(value, "INR", fx_rate=fx_rate, decimals=0)


def unit_cost(value, currency="USD", fx_rate=83):
    """Format a canonical USD unit cost in the requested display mode."""
    mode = normalize_display_currency(currency)
    if mode == "USD":
        return format_money(value, mode, fx_rate, decimals=4)
    if mode == "INR":
        return format_money(value, mode, fx_rate, decimals=2)
    return f"{format_money(value, 'USD', fx_rate, decimals=4)} / {format_money(value, 'INR', fx_rate, decimals=2)}"


def build_currency_display_frame(frame, column_labels, currency="USD", fx_rate=83):
    """Return a display-only dataframe with governed currency values and labels.

    ``column_labels`` maps canonical USD source columns to business labels without
    a currency suffix. Source data is never modified.
    """
    mode = normalize_display_currency(currency)
    result = frame.copy()
    for source, base_label in column_labels.items():
        if source not in frame.columns:
            continue
        insert_at = result.columns.get_loc(source)
        result = result.drop(columns=[source])
        if mode in {"USD", "Both"}:
            result.insert(insert_at, f"{base_label} (USD)", frame[source])
            insert_at += 1
        if mode in {"INR", "Both"}:
            result.insert(insert_at, f"{base_label} (INR)", frame[source] * float(fx_rate))
    return result
