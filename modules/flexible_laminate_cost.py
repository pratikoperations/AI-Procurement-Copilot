"""Controlled should-cost model for Flexible Laminates."""

from __future__ import annotations

import math

import pandas as pd

SUPPORTED_STRUCTURES = {
    "PET / PE": {"PET": 0.35, "PE": 0.60, "process_allowance": 0.05, "layer_count": 2},
    "PET / MetPET / PE": {"PET": 0.25, "MetPET": 0.20, "PE": 0.50, "process_allowance": 0.05, "layer_count": 3},
    "BOPP / CPP": {"BOPP": 0.45, "CPP": 0.50, "process_allowance": 0.05, "layer_count": 2},
}

SUBSTRATE_PRICES_USD_PER_KG = {
    "PET": 1.45,
    "MetPET": 2.10,
    "PE": 1.30,
    "BOPP": 1.38,
    "CPP": 1.42,
}

PRINT_PROFILES = {"Unprinted", "Up to 4 colours", "5–8 colours"}
PRINT_PROCESSES = {"Rotogravure", "Flexographic"}
ADHESIVE_TYPES = {"Solvent-based", "Solvent-free"}


def compounded_yield(printing_loss_pct: float, lamination_loss_pct: float, slitting_loss_pct: float) -> float:
    """Return governed compounded process yield from percentage losses."""
    losses = [printing_loss_pct, lamination_loss_pct, slitting_loss_pct]
    if any(not math.isfinite(float(value)) for value in losses):
        raise ValueError("Flexible Laminates process losses must be finite numbers.")
    if not 0 <= printing_loss_pct <= 8:
        raise ValueError("Printing loss must be between 0% and 8%.")
    if not 0 <= lamination_loss_pct <= 6:
        raise ValueError("Lamination loss must be between 0% and 6%.")
    if not 0 <= slitting_loss_pct <= 5:
        raise ValueError("Slitting loss must be between 0% and 5%.")
    yield_factor = (1 - printing_loss_pct / 100) * (1 - lamination_loss_pct / 100) * (1 - slitting_loss_pct / 100)
    if 1 - yield_factor >= 0.15:
        raise ValueError("Combined effective process loss must remain below 15%.")
    return yield_factor


def tooling_amortisation_per_kg(
    print_profile: str,
    print_process: str,
    number_of_colours: int,
    tooling_cost_per_colour_usd: float,
    tooling_lifetime_volume_kg: float,
    tooling_status: str,
) -> float:
    """Return print-tooling amortisation in USD/kg with fail-closed consistency checks."""
    if print_profile not in PRINT_PROFILES:
        raise ValueError(f"Unsupported print profile '{print_profile}'.")
    if print_process not in PRINT_PROCESSES:
        raise ValueError(f"Unsupported print process '{print_process}'.")
    if not isinstance(number_of_colours, int) or not 0 <= number_of_colours <= 8:
        raise ValueError("Number of colours must be a whole number between 0 and 8.")
    if print_profile == "Unprinted":
        if number_of_colours != 0 or tooling_cost_per_colour_usd != 0:
            raise ValueError("Unprinted laminate must use zero colours and zero tooling cost.")
        return 0.0
    if number_of_colours == 0:
        raise ValueError("Printed laminate requires at least one colour.")
    if tooling_status not in {"New", "Existing", "Not applicable"}:
        raise ValueError("Tooling status must be New, Existing, or Not applicable.")
    if tooling_status == "Not applicable":
        raise ValueError("Printed laminate cannot use Not applicable tooling status.")
    if tooling_cost_per_colour_usd < 0 or not math.isfinite(tooling_cost_per_colour_usd):
        raise ValueError("Tooling cost must be finite and non-negative.")
    if tooling_status == "Existing":
        return 0.0
    if tooling_lifetime_volume_kg <= 0 or not math.isfinite(tooling_lifetime_volume_kg):
        raise ValueError("New tooling requires a positive lifetime production volume in kg.")
    return number_of_colours * tooling_cost_per_colour_usd / tooling_lifetime_volume_kg


def calculate_flexible_laminate_should_cost(
    structure: str = "PET / PE",
    total_micron: float = 70,
    print_profile: str = "Up to 4 colours",
    print_process: str = "Rotogravure",
    number_of_colours: int = 4,
    adhesive_type: str = "Solvent-free",
    printing_loss_pct: float = 3.0,
    lamination_loss_pct: float = 2.0,
    slitting_loss_pct: float = 1.0,
    tooling_cost_per_colour_usd: float = 250.0,
    tooling_lifetime_volume_kg: float = 250000.0,
    tooling_status: str = "New",
    raw_material_shock: float = 0.0,
    freight_shock: float = 0.0,
) -> dict:
    """Calculate a controlled synthetic Flexible Laminates should-cost in USD/kg."""
    if structure not in SUPPORTED_STRUCTURES:
        raise ValueError(f"Unsupported Flexible Laminates structure '{structure}'.")
    if not math.isfinite(float(total_micron)) or not 35 <= float(total_micron) <= 140:
        raise ValueError("Total micron must be between 35 and 140.")
    if adhesive_type not in ADHESIVE_TYPES:
        raise ValueError(f"Unsupported adhesive type '{adhesive_type}'.")

    profile = SUPPORTED_STRUCTURES[structure]
    substrate_components = {}
    for material, share in profile.items():
        if material in {"process_allowance", "layer_count"}:
            continue
        substrate_components[f"{material} Substrate"] = share * SUBSTRATE_PRICES_USD_PER_KG[material] * (1 + raw_material_shock)

    printing_ink = 0.0 if print_profile == "Unprinted" else 0.025 + 0.006 * number_of_colours
    adhesive = 0.075 if adhesive_type == "Solvent-free" else 0.085
    printing_conversion = 0.0 if print_profile == "Unprinted" else (0.12 if print_process == "Rotogravure" else 0.10)
    lamination_conversion = 0.10 if profile["layer_count"] == 2 else 0.16
    recurring_before_loss = sum(substrate_components.values()) + printing_ink + adhesive + printing_conversion + lamination_conversion
    yield_factor = compounded_yield(printing_loss_pct, lamination_loss_pct, slitting_loss_pct)
    gross_recurring = recurring_before_loss / yield_factor
    process_loss_cost = gross_recurring - recurring_before_loss
    tooling = tooling_amortisation_per_kg(
        print_profile,
        print_process,
        number_of_colours,
        tooling_cost_per_colour_usd,
        tooling_lifetime_volume_kg,
        tooling_status,
    )
    freight = 0.08 * (1 + freight_shock)
    subtotal = gross_recurring + tooling + freight
    supplier_margin = subtotal * 0.08
    target = subtotal + supplier_margin

    components = {
        **substrate_components,
        "Printing Ink": printing_ink,
        "Lamination Adhesive": adhesive,
        "Printing Conversion": printing_conversion,
        "Lamination Conversion": lamination_conversion,
        "Wastage / Process Loss": process_loss_cost,
        "Print Tooling Amortisation": tooling,
        "Freight": freight,
        "Supplier Margin": supplier_margin,
    }
    return {
        "commodity": "Flexible Laminates",
        "structure": structure,
        "unit": "kg",
        "layer_count": profile["layer_count"],
        "total_micron": float(total_micron),
        "effective_process_loss_pct": (1 - yield_factor) * 100,
        "components": components,
        "target_unit_cost_usd": target,
    }


def flexible_laminate_should_cost_dataframe(result: dict, annual_volume_kg: float, fx_rate: float) -> pd.DataFrame:
    """Return a business-facing component table for the laminate should-cost result."""
    rows = []
    for component, unit_cost in result["components"].items():
        rows.append({
            "Cost Component": component,
            "Unit Cost USD/kg": unit_cost,
            "Unit Cost INR/kg": unit_cost * fx_rate,
            "Annual Cost USD": unit_cost * annual_volume_kg,
            "Annual Cost INR": unit_cost * annual_volume_kg * fx_rate,
        })
    return pd.DataFrame(rows)
