"""Route should-cost calculations to the selected category engine."""

from modules.flexible_laminate_cost import (
    calculate_flexible_laminate_should_cost,
    flexible_laminate_should_cost_dataframe,
)
from modules.raw_material_cost import calculate_raw_material_should_cost, raw_material_should_cost_dataframe
from modules.should_cost import calculate_packaging_should_cost, should_cost_dataframe


def _controlled_kraft_gsm(value):
    """Return an exact whole-number GSM without silently truncating decimals."""
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Kraft Paper GSM must be numeric.") from exc
    if not numeric.is_integer():
        raise ValueError("Kraft Paper GSM must be a whole-number controlled profile.")
    return int(numeric)


def calculate_category_should_cost(assumptions):
    """Return category-specific should-cost dictionary and dataframe."""
    category = assumptions.get("category", "Packaging Procurement")
    volume = assumptions["annual_volume"] * (1 + assumptions.get("demand_change", 0.0))
    if category == "Raw Material Procurement":
        commodity = assumptions.get("commodity", "PET Resin")
        kwargs = {}
        if commodity == "Kraft Paper":
            kwargs = {
                "kraft_variant": assumptions.get("kraft_variant", "Recycled Kraft"),
                "gsm": _controlled_kraft_gsm(assumptions.get("kraft_gsm", 150)),
                "strength_grade": assumptions.get("kraft_strength_grade", "22 BF"),
            }
        result = calculate_raw_material_should_cost(
            commodity,
            commodity_shock=assumptions.get("raw_material_shock", 0.0),
            freight_shock=assumptions.get("freight_shock", 0.0),
            **kwargs,
        )
        frame = raw_material_should_cost_dataframe(result, volume, assumptions["fx_rate"])
    else:
        commodity = assumptions.get("commodity", "Corrugated Board")
        if commodity == "Flexible Laminates":
            result = calculate_flexible_laminate_should_cost(
                structure=assumptions.get("laminate_structure", "PET / PE"),
                total_micron=assumptions.get("laminate_total_micron", 70),
                print_profile=assumptions.get("laminate_print_profile", "Up to 4 colours"),
                print_process=assumptions.get("laminate_print_process", "Rotogravure"),
                number_of_colours=assumptions.get("laminate_number_of_colours", 4),
                adhesive_type=assumptions.get("laminate_adhesive_type", "Solvent-free"),
                printing_loss_pct=assumptions.get("laminate_printing_loss_pct", 3.0),
                lamination_loss_pct=assumptions.get("laminate_lamination_loss_pct", 2.0),
                slitting_loss_pct=assumptions.get("laminate_slitting_loss_pct", 1.0),
                tooling_cost_per_colour_usd=assumptions.get("laminate_tooling_cost_per_colour_usd", 250.0),
                tooling_lifetime_volume_kg=assumptions.get("laminate_tooling_lifetime_volume_kg", 250000.0),
                tooling_status=assumptions.get("laminate_tooling_status", "New"),
                existing_tooling_available=assumptions.get("laminate_existing_tooling_available", "Not applicable"),
                raw_material_shock=assumptions.get("raw_material_shock", 0.0),
                freight_shock=assumptions.get("freight_shock", 0.0),
            )
            frame = flexible_laminate_should_cost_dataframe(result, volume, assumptions["fx_rate"])
        else:
            result = calculate_packaging_should_cost(
                raw_material_shock=assumptions.get("raw_material_shock", 0.0),
                freight_shock=assumptions.get("freight_shock", 0.0),
            )
            frame = should_cost_dataframe(result, volume, assumptions["fx_rate"])
    return result, frame
