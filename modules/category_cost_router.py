"""Route should-cost calculations to the selected category engine."""

from modules.raw_material_cost import calculate_raw_material_should_cost, raw_material_should_cost_dataframe
from modules.should_cost import calculate_packaging_should_cost, should_cost_dataframe


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
                "gsm": int(assumptions.get("kraft_gsm", 150)),
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
        result = calculate_packaging_should_cost(
            raw_material_shock=assumptions.get("raw_material_shock", 0.0),
            freight_shock=assumptions.get("freight_shock", 0.0),
        )
        frame = should_cost_dataframe(result, volume, assumptions["fx_rate"])
    return result, frame
