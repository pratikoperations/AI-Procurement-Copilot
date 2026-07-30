"""Commodity-aware raw-material should-cost engine."""

import pandas as pd

COMMODITY_BASELINES = {
    "PET Resin": {"commodity_index": 1.05, "conversion_premium": 0.08, "freight": 0.05, "duty": 0.03, "quality_premium": 0.02, "supplier_margin": 0.04},
    "Polyethylene": {"commodity_index": 1.12, "conversion_premium": 0.07, "freight": 0.05, "duty": 0.03, "quality_premium": 0.02, "supplier_margin": 0.04},
    "Polypropylene": {"commodity_index": 1.08, "conversion_premium": 0.07, "freight": 0.05, "duty": 0.03, "quality_premium": 0.02, "supplier_margin": 0.04},
    "Aluminium Foil": {"commodity_index": 2.35, "conversion_premium": 0.42, "freight": 0.08, "duty": 0.10, "quality_premium": 0.09, "supplier_margin": 0.12},
    "Steel": {"commodity_index": 0.82, "conversion_premium": 0.16, "freight": 0.06, "duty": 0.05, "quality_premium": 0.03, "supplier_margin": 0.05},
    "Copper": {"commodity_index": 8.45, "conversion_premium": 0.55, "freight": 0.10, "duty": 0.18, "quality_premium": 0.12, "supplier_margin": 0.20},
    "Kraft Paper": {"commodity_index": 0.61, "conversion_premium": 0.09, "freight": 0.06, "duty": 0.00, "quality_premium": 0.04, "supplier_margin": 0.05},
}

KRAFT_VARIANT_ADJUSTMENTS = {
    "Recycled Kraft": {"commodity_index": 0.00, "quality_premium": 0.00},
    "Virgin Kraft": {"commodity_index": 0.11, "quality_premium": 0.03},
}
KRAFT_STRENGTH_PREMIUM = {"18 BF": 0.00, "22 BF": 0.025, "28 BF": 0.055}
KRAFT_GSM_PREMIUM = {120: 0.00, 150: 0.015, 180: 0.03}

LABELS = {
    "commodity_index": "Commodity Index",
    "conversion_premium": "Conversion / Producer Premium",
    "freight": "Freight",
    "duty": "Duty / Import Cost",
    "quality_premium": "Grade / Quality Premium",
    "supplier_margin": "Supplier Margin",
}
KRAFT_LABELS = {
    **LABELS,
    "commodity_index": "Paper Index",
    "conversion_premium": "Mill / Producer Premium",
}


def _kraft_inputs(inputs, kraft_variant, gsm, strength_grade):
    base = dict(inputs or COMMODITY_BASELINES["Kraft Paper"])
    if kraft_variant not in KRAFT_VARIANT_ADJUSTMENTS:
        raise ValueError(f"Unsupported Kraft Paper variant '{kraft_variant}'.")
    if gsm not in KRAFT_GSM_PREMIUM:
        raise ValueError(f"Unsupported Kraft Paper GSM '{gsm}'.")
    if strength_grade not in KRAFT_STRENGTH_PREMIUM:
        raise ValueError(f"Unsupported Kraft Paper strength grade '{strength_grade}'.")
    adjustment = KRAFT_VARIANT_ADJUSTMENTS[kraft_variant]
    base["commodity_index"] += adjustment["commodity_index"]
    base["quality_premium"] += adjustment["quality_premium"] + KRAFT_GSM_PREMIUM[gsm] + KRAFT_STRENGTH_PREMIUM[strength_grade]
    return base


def calculate_raw_material_should_cost(
    commodity,
    commodity_shock=0.0,
    freight_shock=0.0,
    fx_shock=0.0,
    inputs=None,
    kraft_variant="Recycled Kraft",
    gsm=150,
    strength_grade="22 BF",
):
    """Calculate delivered raw-material should-cost per kg using explicit components."""
    if commodity not in COMMODITY_BASELINES:
        supported = ", ".join(sorted(COMMODITY_BASELINES))
        raise ValueError(f"Unsupported raw-material commodity '{commodity}'. Supported commodities: {supported}")
    base = _kraft_inputs(inputs, kraft_variant, gsm, strength_grade) if commodity == "Kraft Paper" else dict(inputs or COMMODITY_BASELINES[commodity])
    result = {}
    for key, value in base.items():
        adjusted = float(value)
        if key == "commodity_index":
            adjusted *= 1 + commodity_shock
        if key == "freight":
            adjusted *= 1 + freight_shock
        if key in {"commodity_index", "conversion_premium", "freight", "duty"}:
            adjusted *= 1 + fx_shock
        result[key] = adjusted
    result["target_unit_cost_usd"] = sum(result.values())
    result["commodity"] = commodity
    if commodity == "Kraft Paper":
        result.update({"kraft_variant": kraft_variant, "gsm": gsm, "strength_grade": strength_grade, "downstream_link": "Corrugated Board"})
    return result


def raw_material_should_cost_dataframe(should_cost, annual_volume, fx_rate):
    total = float(should_cost.get("target_unit_cost_usd", 0.0))
    rows = []
    labels = KRAFT_LABELS if should_cost.get("commodity") == "Kraft Paper" else LABELS
    for key, label in labels.items():
        value = float(should_cost.get(key, 0.0))
        rows.append({
            "Component": label,
            "Unit Cost USD": value,
            "Contribution %": value / total * 100 if total else 0,
            "Annual Impact USD": value * annual_volume,
            "Annual Impact INR": value * annual_volume * fx_rate,
        })
    return pd.DataFrame(rows)
