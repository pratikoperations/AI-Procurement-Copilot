"""Pure reconciliation checks for authoritative calculation outputs."""

from __future__ import annotations

import math


def _finite(value, name):
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError(f"{name} must be finite.")
    return numeric


def reconcile_component_total(result, *, components_key="components", total_key="target_unit_cost_usd", tolerance=1e-9):
    components = result.get(components_key, {})
    if not isinstance(components, dict):
        raise ValueError("Authoritative components must be a dictionary.")
    component_total = sum(_finite(value, str(name)) for name, value in components.items())
    authoritative_total = _finite(result[total_key], total_key)
    difference = component_total - authoritative_total
    return {
        "passed": math.isclose(component_total, authoritative_total, rel_tol=0.0, abs_tol=tolerance),
        "component_total": component_total,
        "authoritative_total": authoritative_total,
        "difference": difference,
    }


def reconcile_annual_value(unit_value, annual_volume, annual_value, *, tolerance=1e-6):
    expected = _finite(unit_value, "unit_value") * _finite(annual_volume, "annual_volume")
    actual = _finite(annual_value, "annual_value")
    return {
        "passed": math.isclose(expected, actual, rel_tol=0.0, abs_tol=tolerance),
        "expected": expected,
        "actual": actual,
        "difference": expected - actual,
    }


def reconcile_currency(usd_value, fx_rate, inr_value, *, tolerance=1e-6):
    expected = _finite(usd_value, "usd_value") * _finite(fx_rate, "fx_rate")
    actual = _finite(inr_value, "inr_value")
    return {
        "passed": math.isclose(expected, actual, rel_tol=0.0, abs_tol=tolerance),
        "expected": expected,
        "actual": actual,
        "difference": expected - actual,
    }


def assert_reconciled(checks):
    failures = [name for name, check in checks.items() if not check.get("passed")]
    if failures:
        raise ValueError("Explorer reconciliation failed: " + ", ".join(failures))
    return True
