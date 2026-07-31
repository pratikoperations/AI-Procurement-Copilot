"""Controlled should-cost model for Flexible Laminates."""

from __future__ import annotations

import math

import pandas as pd

SUPPORTED_STRUCTURES = {
    "PET / PE": {"PET": 0.37, "PE": 0.63, "layer_count": 2},
    "PET / MetPET / PE": {"PET": 0.27, "MetPET": 0.21, "PE": 0.52, "layer_count": 3},
    "BOPP / CPP": {"BOPP": 0.47, "CPP": 0.53, "layer_count": 2},
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
TOOLING_AVAILABILITY = {"Yes", "No", "Not assessed", "Not applicable"}


def _controlled_colour_count(value) -> int:
    """Return an exact integer colour count without silent truncation."""
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Number of colours must be numeric.") from exc
    if not math.isfinite(numeric) or not numeric.is_integer():
        raise ValueError("Number of colours must be a whole number between 0 and 8.")
    count = int(numeric)
    if not 0 <= count <= 8:
        raise ValueError("Number of colours must be a whole number between 0 and 8.")
    return count


def validate_print_profile_colours(print_profile: str, number_of_colours) -> int:
    """Validate controlled print-profile and colour-count combinations."""
    if print_profile not in PRINT_PROFILES:
        raise ValueError(f"Unsupported print profile '{print_profile}'.")
    count = _controlled_colour_count(number_of_colours)
    valid = (
        (print_profile == "Unprinted" and count == 0)
        or (print_profile == "Up to 4 colours" and 1 <= count <= 4)
        or (print_profile == "5–8 colours" and 5 <= count <= 8)
    )
    if not valid:
        raise ValueError(f"Print profile '{print_profile}' is inconsistent with {count} colours.")
    return count


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


def _validate_tooling_contract(
    print_profile: str,
    tooling_status: str,
    existing_tooling_available: str,
    tooling_cost_per_colour_usd: float,
) -> None:
    """Enforce status-to-evidence consistency for print tooling."""
    if tooling_status not in {"New", "Existing", "Not applicable"}:
        raise ValueError("Tooling status must be New, Existing, or Not applicable.")
    if existing_tooling_available not in TOOLING_AVAILABILITY:
        raise ValueError("Existing tooling availability must be Yes, No, Not assessed, or Not applicable.")
    if tooling_cost_per_colour_usd < 0 or not math.isfinite(float(tooling_cost_per_colour_usd)):
        raise ValueError("Tooling cost must be finite and non-negative.")

    if print_profile == "Unprinted":
        if tooling_status != "Not applicable" or existing_tooling_available != "Not applicable":
            raise ValueError("Unprinted laminate must use Not applicable tooling status and availability.")
        if tooling_cost_per_colour_usd != 0:
            raise ValueError("Unprinted laminate must use zero tooling cost.")
        return

    if tooling_status == "New":
        if existing_tooling_available != "Not applicable":
            raise ValueError("New tooling requires Existing Tooling Available to be Not applicable.")
        return

    if tooling_status == "Existing":
        if existing_tooling_available not in {"Yes", "No", "Not assessed"}:
            raise ValueError("Existing tooling availability must be Yes, No, or Not assessed.")
        return

    raise ValueError("Printed laminate tooling status must be New or Existing.")


def tooling_amortisation_per_kg(
    print_profile: str,
    print_process: str,
    number_of_colours,
    tooling_cost_per_colour_usd: float,
    tooling_lifetime_volume_kg: float,
    tooling_status: str,
    existing_tooling_available: str = "Not applicable",
) -> float:
    """Return print-tooling amortisation in USD/kg with fail-closed evidence controls."""
    count = validate_print_profile_colours(print_profile, number_of_colours)
    if print_process not in PRINT_PROCESSES:
        raise ValueError(f"Unsupported print process '{print_process}'.")
    _validate_tooling_contract(
        print_profile,
        tooling_status,
        existing_tooling_available,
        tooling_cost_per_colour_usd,
    )
    if print_profile == "Unprinted":
        return 0.0
    if tooling_status == "Existing":
        if existing_tooling_available != "Yes":
            raise ValueError("Existing tooling requires explicit availability confirmation before zero amortisation.")
        return 0.0
    if tooling_lifetime_volume_kg <= 0 or not math.isfinite(float(tooling_lifetime_volume_kg)):
        raise ValueError("New tooling requires a positive lifetime production volume in kg.")
    return count * tooling_cost_per_colour_usd / tooling_lifetime_volume_kg


def calculate_flexible_laminate_should_cost(
    structure: str = "PET / PE",
    total_micron: float = 70,
    print_profile: str = "Up to 4 colours",
    print_process: str = "Rotogravure",
    number_of_colours=4,
    adhesive_type: str = "Solvent-free",
    printing_loss_pct: float = 3.0,
    lamination_loss_pct: float = 2.0,
    slitting_loss_pct: float = 1.0,
    tooling_cost_per_colour_usd: float = 250.0,
    tooling_lifetime_volume_kg: float = 250000.0,
    tooling_status: str = "New",
    existing_tooling_available: str = "Not applicable",
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
    count = validate_print_profile_colours(print_profile, number_of_colours)

    profile = SUPPORTED_STRUCTURES[structure]
    material_shares = {key: value for key, value in profile.items() if key != "layer_count"}
    if not math.isclose(sum(material_shares.values()), 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError("Controlled laminate substrate mass shares must reconcile exactly to 100%.")
    substrate_components = {
        f"{material} Substrate": share * SUBSTRATE_PRICES_USD_PER_KG[material] * (1 + raw_material_shock)
        for material, share in material_shares.items()
    }

    printing_ink = 0.0 if print_profile == "Unprinted" else 0.025 + 0.006 * count
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
        count,
        tooling_cost_per_colour_usd,
        tooling_lifetime_volume_kg,
        tooling_status,
        existing_tooling_available,
    )
    freight = 0.08 * (1 + freight_shock)
    subtotal = gross_recurring + tooling + freight
    supplier_margin = subtotal * 0.08
    target = subtotal + supplier_margin

    components = {
        **substrate_components,
        "Printing Ink Process Allowance": printing_ink,
        "Lamination Adhesive Process Allowance": adhesive,
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
        "total_micron_basis": "Controlled metadata only; C2 uses fixed synthetic mass-share profiles and does not infer physical mass from micron.",
        "material_mass_share_total": sum(material_shares.values()),
        "effective_process_loss_pct": (1 - yield_factor) * 100,
        "components": components,
        "target_unit_cost_usd": target,
    }


def flexible_laminate_should_cost_dataframe(result: dict, annual_volume_kg: float, fx_rate: float) -> pd.DataFrame:
    """Return a business-facing component table for the laminate should-cost result."""
    return pd.DataFrame([
        {
            "Cost Component": component,
            "Unit Cost USD/kg": unit_cost,
            "Unit Cost INR/kg": unit_cost * fx_rate,
            "Annual Cost USD": unit_cost * annual_volume_kg,
            "Annual Cost INR": unit_cost * annual_volume_kg * fx_rate,
        }
        for component, unit_cost in result["components"].items()
    ])
