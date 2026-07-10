"""Packaging should-cost engine."""

import pandas as pd


DEFAULT_PACKAGING_SHOULD_COST = {
    "substrate_raw_material": 0.240,
    "resin_film_foil": 0.000,
    "ink_coating": 0.012,
    "adhesive_solvent": 0.000,
    "conversion": 0.070,
    "printing": 0.025,
    "lamination_slitting": 0.000,
    "tooling_plate_amortization": 0.008,
    "scrap_wastage": 0.015,
    "freight_buffer": 0.025,
    "factory_overhead": 0.018,
    "sga_margin": 0.017,
}

COMPONENT_LABELS = {
    "substrate_raw_material": "Substrate / Paper",
    "resin_film_foil": "Resin / Film / Foil",
    "ink_coating": "Ink / Coating",
    "adhesive_solvent": "Adhesive / Solvent",
    "conversion": "Conversion",
    "printing": "Printing",
    "lamination_slitting": "Lamination / Slitting",
    "tooling_plate_amortization": "Tooling / Plate Amortization",
    "scrap_wastage": "Scrap / Wastage",
    "freight_buffer": "Freight Buffer",
    "factory_overhead": "Factory Overhead",
    "sga_margin": "SG&A + Margin",
}


def calculate_packaging_should_cost(inputs=None, raw_material_shock=0.0, freight_shock=0.0, fx_shock=0.0, indexation=0.0):
    """Calculate packaging should-cost from auditable component assumptions."""
    inputs = inputs or DEFAULT_PACKAGING_SHOULD_COST
    result = {}

    raw_keys = ["substrate_raw_material", "resin_film_foil"]
    freight_keys = ["freight_buffer"]

    for key, value in inputs.items():
        adjusted = float(value)
        if key in raw_keys:
            adjusted *= 1 + raw_material_shock + indexation
        if key in freight_keys:
            adjusted *= 1 + freight_shock
        result[key] = adjusted

    result["target_unit_cost_usd"] = sum(result.values()) * (1 + fx_shock)
    return result


def should_cost_dataframe(should_cost, annual_volume, fx_rate):
    """Return a dataframe showing unit and annual impact by should-cost component."""
    rows = []
    total = should_cost.get("target_unit_cost_usd", 0.0)

    for key, label in COMPONENT_LABELS.items():
        unit_cost = should_cost.get(key, 0.0)
        rows.append(
            {
                "Component": label,
                "Unit Cost USD": unit_cost,
                "Contribution %": (unit_cost / total * 100) if total else 0,
                "Annual Impact USD": unit_cost * annual_volume,
                "Annual Impact INR": unit_cost * annual_volume * fx_rate,
            }
        )

    return pd.DataFrame(rows)
