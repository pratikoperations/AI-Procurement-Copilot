"""Governed Steel should-cost and currency-normalization engine for C3.

All calculations use USD/kg as the sole governed calculation path. INR
values are deterministic conversions from one positive user-controlled
USD/INR assumption. Inputs and defaults are controlled synthetic
demonstration assumptions, not live market data or supplier evidence.
"""

from __future__ import annotations

import math
from numbers import Real

import pandas as pd

SUPPORTED_STEEL_PROFILES = {
    "CR_COIL_COMMERCIAL": {"zinc_required": False, "paint_required": False},
    "GI_COIL_Z120": {"zinc_required": True, "paint_required": False},
    "PPGI_COIL_Z120": {"zinc_required": True, "paint_required": True},
}
SUPPORTED_QUOTATION_CURRENCIES = {"USD", "INR"}
SUPPORTED_DISPLAY_MODES = {"USD", "INR", "Both"}

# Controlled synthetic C3.2 defaults. These are deliberately explicit and
# versioned in code; they are not live commodity, FX, mill, or supplier data.
CONTROLLED_STEEL_COST_ASSUMPTIONS = {
    "base_steel_usd_per_kg": 0.72,
    "profile_premium_usd_per_kg": 0.05,
    "rolling_conversion_usd_per_kg": 0.10,
    "zinc_cost_usd_per_kg": 0.00,
    "paint_treatment_usd_per_kg": 0.00,
    "energy_surcharge_usd_per_kg": 0.04,
    "yield_pct": 96.0,
    "slitting_cutting_usd_per_kg": 0.025,
    "packing_usd_per_kg": 0.015,
    "freight_usd_per_kg": 0.045,
    "sourcing_route": "Domestic",
    "import_duty_pct": 0.0,
    "supplier_margin_pct": 8.0,
}


def _finite_number(name: str, value, *, positive: bool = False, non_negative: bool = False) -> float:
    """Return a finite float or fail closed with a governed field message."""
    if value is None or isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a numeric value.")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError(f"{name} must be a finite numeric value.")
    if positive and numeric <= 0:
        raise ValueError(f"{name} must be greater than zero.")
    if non_negative and numeric < 0:
        raise ValueError(f"{name} must be non-negative.")
    return numeric


def validate_usd_inr_fx_rate(fx_rate) -> float:
    """Validate the single governed USD/INR demonstration assumption."""
    return _finite_number("USD/INR FX rate", fx_rate, positive=True)


def _validate_profile_applicability(profile_id: str, zinc_cost: float, paint_cost: float) -> None:
    profile = SUPPORTED_STEEL_PROFILES[profile_id]
    if profile["zinc_required"]:
        if zinc_cost <= 0:
            raise ValueError(f"Profile {profile_id} requires a positive zinc cost input.")
    elif zinc_cost != 0:
        raise ValueError(f"Profile {profile_id} requires zinc cost to be zero.")

    if profile["paint_required"]:
        if paint_cost <= 0:
            raise ValueError(f"Profile {profile_id} requires a positive paint or treatment cost input.")
    elif paint_cost != 0:
        raise ValueError(f"Profile {profile_id} requires paint or treatment cost to be zero.")


def calculate_steel_should_cost(
    profile_id: str,
    annual_volume_kg,
    *,
    base_steel_usd_per_kg,
    profile_premium_usd_per_kg,
    rolling_conversion_usd_per_kg,
    zinc_cost_usd_per_kg,
    paint_treatment_usd_per_kg,
    energy_surcharge_usd_per_kg,
    yield_pct,
    slitting_cutting_usd_per_kg,
    packing_usd_per_kg,
    freight_usd_per_kg,
    sourcing_route: str,
    import_duty_pct,
    supplier_margin_pct,
) -> dict:
    """Calculate deterministic governed Steel should-cost in USD/kg.

    Yield loss applies only to the recurring material/conversion/energy block.
    Import duty applies only when ``sourcing_route`` is ``Import`` and is
    calculated on the pre-duty landed subtotal. Supplier margin applies after
    duty. Annual values are derived from the final USD/kg result.
    """
    if profile_id not in SUPPORTED_STEEL_PROFILES:
        raise ValueError(f"Unsupported Steel profile '{profile_id}'.")

    annual_volume = _finite_number("Annual volume kg", annual_volume_kg, positive=True)
    component_values = {
        "Base Steel": _finite_number("Base steel cost", base_steel_usd_per_kg, non_negative=True),
        "Controlled Profile / Grade Premium": _finite_number(
            "Profile or grade premium", profile_premium_usd_per_kg, non_negative=True
        ),
        "Rolling / Conversion Premium": _finite_number(
            "Rolling or conversion premium", rolling_conversion_usd_per_kg, non_negative=True
        ),
        "Zinc Coating": _finite_number("Zinc coating cost", zinc_cost_usd_per_kg, non_negative=True),
        "Paint / Treatment": _finite_number(
            "Paint or treatment cost", paint_treatment_usd_per_kg, non_negative=True
        ),
        "Energy Surcharge": _finite_number(
            "Energy surcharge", energy_surcharge_usd_per_kg, non_negative=True
        ),
        "Slitting / Cutting": _finite_number(
            "Slitting or cutting cost", slitting_cutting_usd_per_kg, non_negative=True
        ),
        "Packing": _finite_number("Packing cost", packing_usd_per_kg, non_negative=True),
        "Freight": _finite_number("Freight cost", freight_usd_per_kg, non_negative=True),
    }
    _validate_profile_applicability(
        profile_id,
        component_values["Zinc Coating"],
        component_values["Paint / Treatment"],
    )

    governed_yield_pct = _finite_number("Yield percent", yield_pct, positive=True)
    if governed_yield_pct > 100:
        raise ValueError("Yield percent must be greater than zero and no more than 100.")
    governed_margin_pct = _finite_number("Supplier margin percent", supplier_margin_pct, non_negative=True)
    if governed_margin_pct >= 100:
        raise ValueError("Supplier margin percent must be at least zero and below 100.")
    governed_duty_pct = _finite_number("Import duty percent", import_duty_pct, non_negative=True)
    if governed_duty_pct > 100:
        raise ValueError("Import duty percent must be between zero and 100.")
    if sourcing_route not in {"Domestic", "Import"}:
        raise ValueError("Sourcing route must be Domestic or Import.")
    if sourcing_route == "Domestic" and governed_duty_pct != 0:
        raise ValueError("Domestic sourcing requires import duty to be zero.")

    recurring_names = (
        "Base Steel",
        "Controlled Profile / Grade Premium",
        "Rolling / Conversion Premium",
        "Zinc Coating",
        "Paint / Treatment",
        "Energy Surcharge",
    )
    recurring_net = sum(component_values[name] for name in recurring_names)
    recurring_gross = recurring_net / (governed_yield_pct / 100.0)
    yield_loss_effect = recurring_gross - recurring_net

    landed_pre_duty = (
        recurring_gross
        + component_values["Slitting / Cutting"]
        + component_values["Packing"]
        + component_values["Freight"]
    )
    duty = landed_pre_duty * governed_duty_pct / 100.0 if sourcing_route == "Import" else 0.0
    subtotal_before_margin = landed_pre_duty + duty
    supplier_margin = subtotal_before_margin * governed_margin_pct / 100.0
    target_unit_cost_usd = subtotal_before_margin + supplier_margin

    components = {
        "Base Steel": component_values["Base Steel"],
        "Controlled Profile / Grade Premium": component_values["Controlled Profile / Grade Premium"],
        "Rolling / Conversion Premium": component_values["Rolling / Conversion Premium"],
        "Zinc Coating": component_values["Zinc Coating"],
        "Paint / Treatment": component_values["Paint / Treatment"],
        "Energy Surcharge": component_values["Energy Surcharge"],
        "Yield-Loss Effect": yield_loss_effect,
        "Slitting / Cutting": component_values["Slitting / Cutting"],
        "Packing": component_values["Packing"],
        "Freight": component_values["Freight"],
        "Import Duty": duty,
        "Supplier Margin": supplier_margin,
    }
    if not math.isclose(sum(components.values()), target_unit_cost_usd, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError("Steel should-cost components failed deterministic reconciliation.")

    return {
        "commodity": "Steel",
        "profile_id": profile_id,
        "unit": "kg",
        "calculation_currency": "USD",
        "comparison_unit": "USD/kg",
        "annual_volume_kg": annual_volume,
        "sourcing_route": sourcing_route,
        "yield_pct": governed_yield_pct,
        "import_duty_pct": governed_duty_pct,
        "supplier_margin_pct": governed_margin_pct,
        "components": components,
        "target_unit_cost_usd": target_unit_cost_usd,
        "annual_value_usd": target_unit_cost_usd * annual_volume,
        "assumption_boundary": "Controlled synthetic demonstration assumptions; not live market data.",
    }


def add_steel_currency_values(result: dict, fx_rate, display_mode: str = "Both") -> dict:
    """Add deterministic currency fields to a Steel should-cost result."""
    fx = validate_usd_inr_fx_rate(fx_rate)
    if display_mode not in SUPPORTED_DISPLAY_MODES:
        raise ValueError(f"Unsupported Steel display mode '{display_mode}'.")
    unit_usd = _finite_number("Target unit cost USD/kg", result.get("target_unit_cost_usd"), non_negative=True)
    annual_usd = _finite_number("Annual value USD", result.get("annual_value_usd"), non_negative=True)
    enriched = dict(result)
    enriched.update(
        {
            "display_mode": display_mode,
            "usd_inr_fx_rate": fx,
            "unit_cost_usd_per_kg": unit_usd,
            "unit_cost_inr_per_kg": unit_usd * fx,
            "annual_value_usd": annual_usd,
            "annual_value_inr": annual_usd * fx,
        }
    )
    return enriched


def normalize_steel_supplier_quotation(
    quoted_unit_price,
    quotation_currency: str,
    annual_volume_kg,
    fx_rate,
    display_mode: str = "Both",
) -> dict:
    """Normalize a USD or INR supplier quotation through USD/kg."""
    quoted_price = _finite_number("Quoted unit price", quoted_unit_price, non_negative=True)
    annual_volume = _finite_number("Annual volume kg", annual_volume_kg, positive=True)
    fx = validate_usd_inr_fx_rate(fx_rate)
    if quotation_currency not in SUPPORTED_QUOTATION_CURRENCIES:
        raise ValueError(f"Unsupported Steel quotation currency '{quotation_currency}'.")
    if display_mode not in SUPPORTED_DISPLAY_MODES:
        raise ValueError(f"Unsupported Steel display mode '{display_mode}'.")

    normalized_usd = quoted_price if quotation_currency == "USD" else quoted_price / fx
    equivalent_inr = normalized_usd * fx
    annual_usd = normalized_usd * annual_volume
    annual_inr = annual_usd * fx
    return {
        "quotation_currency": quotation_currency,
        "quoted_unit_price": quoted_price,
        "display_mode": display_mode,
        "usd_inr_fx_rate": fx,
        "normalized_usd_per_kg": normalized_usd,
        "equivalent_inr_per_kg": equivalent_inr,
        "annual_value_usd": annual_usd,
        "annual_value_inr": annual_inr,
    }


def steel_should_cost_dataframe(result: dict, fx_rate, display_mode: str = "Both") -> pd.DataFrame:
    """Return governed numeric Steel component fields for the selected display mode."""
    fx = validate_usd_inr_fx_rate(fx_rate)
    if display_mode not in SUPPORTED_DISPLAY_MODES:
        raise ValueError(f"Unsupported Steel display mode '{display_mode}'.")
    annual_volume = _finite_number("Annual volume kg", result.get("annual_volume_kg"), positive=True)
    rows = []
    for component, unit_cost_usd in result["components"].items():
        row = {"Cost Component": component}
        if display_mode in {"USD", "Both"}:
            row["Unit Cost USD/kg"] = unit_cost_usd
            row["Annual Cost USD"] = unit_cost_usd * annual_volume
        if display_mode in {"INR", "Both"}:
            row["Unit Cost INR/kg"] = unit_cost_usd * fx
            row["Annual Cost INR"] = unit_cost_usd * annual_volume * fx
        rows.append(row)
    return pd.DataFrame(rows)
