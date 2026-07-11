"""Commodity-aware raw-material should-cost engine."""

import pandas as pd

COMMODITY_BASELINES = {
    "PET Resin": {"commodity_index": 1.05, "conversion_premium": 0.08, "freight": 0.05, "duty": 0.03, "quality_premium": 0.02, "supplier_margin": 0.04},
    "Polyethylene": {"commodity_index": 1.12, "conversion_premium": 0.07, "freight": 0.05, "duty": 0.03, "quality_premium": 0.02, "supplier_margin": 0.04},
    "Polypropylene": {"commodity_index": 1.08, "conversion_premium": 0.07, "freight": 0.05, "duty": 0.03, "quality_premium": 0.02, "supplier_margin": 0.04},
    "Aluminium Foil": {"commodity_index": 2.35, "conversion_premium": 0.42, "freight": 0.08, "duty": 0.10, "quality_premium": 0.09, "supplier_margin": 0.12},
    "Steel": {"commodity_index": 0.82, "conversion_premium": 0.16, "freight": 0.06, "duty": 0.05, "quality_premium": 0.03, "supplier_margin": 0.05},
    "Copper": {"commodity_index": 8.45, "conversion_premium": 0.55, "freight": 0.10, "duty": 0.18, "quality_premium": 0.12, "supplier_margin": 0.20},
}

LABELS = {
    "commodity_index": "Commodity Index",
    "conversion_premium": "Conversion / Producer Premium",
    "freight": "Freight",
    "duty": "Duty / Import Cost",
    "quality_premium": "Grade / Quality Premium",
    "supplier_margin": "Supplier Margin",
}


def calculate_raw_material_should_cost(commodity, commodity_shock=0.0, freight_shock=0.0, fx_shock=0.0, inputs=None):
    """Calculate delivered raw-material should-cost per kg using explicit components."""
    base = dict(inputs or COMMODITY_BASELINES.get(commodity, COMMODITY_BASELINES["PET Resin"]))
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
    return result


def raw_material_should_cost_dataframe(should_cost, annual_volume, fx_rate):
    total = float(should_cost.get("target_unit_cost_usd", 0.0))
    rows = []
    for key, label in LABELS.items():
        value = float(should_cost.get(key, 0.0))
        rows.append({
            "Component": label,
            "Unit Cost USD": value,
            "Contribution %": value / total * 100 if total else 0,
            "Annual Impact USD": value * annual_volume,
            "Annual Impact INR": value * annual_volume * fx_rate,
        })
    return pd.DataFrame(rows)
