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


def money_usd(value):
    return f"${value:,.0f}"


def money_inr(value, fx_rate):
    return f"₹{value * fx_rate:,.0f}"


def unit_cost(value, currency="USD", fx_rate=83):
    if currency == "USD":
        return f"${value:.4f}"
    if currency == "INR":
        return f"₹{value * fx_rate:.2f}"
    return f"${value:.4f} / ₹{value * fx_rate:.2f}"
