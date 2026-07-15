"""Presentation helpers for governed procurement quantity units."""

import pandas as pd


def canonical_unit(unit):
    """Return a stable canonical unit token."""
    value = str(unit or "unit").strip().lower()
    return value or "unit"


def display_unit(unit, quantity=None):
    """Return a human-readable unit label without changing its calculation basis."""
    value = canonical_unit(unit)
    if value == "piece":
        return "piece" if quantity == 1 else "pieces"
    return value


def annual_volume_label(unit):
    """Return the governed sidebar label for annual volume."""
    return f"Annual Volume ({display_unit(unit)})"


def format_annual_volume(volume, unit):
    """Format annual volume with its canonical business unit."""
    quantity = float(volume)
    return f"{quantity:,.0f} {display_unit(unit, quantity)}"


def quantity_basis_caption(volume, unit):
    """Return a readable quantity-basis caption; tonne equivalence is display-only."""
    base = f"Canonical quantity basis: {format_annual_volume(volume, unit)}"
    if canonical_unit(unit) == "kg":
        return f"{base} ({float(volume) / 1000:,.3f} metric tonnes)"
    return base


def add_annual_volume_metadata(frame, annual_volume=None, annual_volume_unit=None):
    """Add readable quantity metadata to a copy of a report DataFrame."""
    result = frame.copy()
    if annual_volume is None or annual_volume_unit is None:
        return result
    unit = canonical_unit(annual_volume_unit)
    result["Annual Volume"] = float(annual_volume)
    result["Annual Volume Unit"] = unit
    result["Quantity Basis"] = format_annual_volume(annual_volume, unit)
    return result
