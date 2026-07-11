"""Production raw-material category engine."""

from modules.commodity_library import get_commodities, get_commodity_profile

CATEGORY_NAME = "Raw Material Procurement"
ENGINE_STATUS = "Active"


def get_engine_profile(commodity=None):
    """Return production raw-material engine metadata."""
    commodities = get_commodities(CATEGORY_NAME)
    selected = commodity if commodity in commodities else commodities[0]
    profile = get_commodity_profile(CATEGORY_NAME, selected)
    return {
        "category": CATEGORY_NAME,
        "category_name": CATEGORY_NAME,
        "engine_status": ENGINE_STATUS,
        "selected_commodity": selected,
        "commodity_group": profile.get("family", "Raw Materials"),
        "commodities": commodities,
        "cost_model": "Commodity Index + Conversion Premium + Freight + Duty + FX + Risk-Adjusted TCO",
        "risk_model": "Volatility, import dependency, concentration, substitution, FX, quality, capacity, and continuity risk",
        "unit": profile.get("unit", "kg"),
        "units": [profile.get("unit", "kg")],
        "currency": "USD",
        "primary_cost_drivers": profile.get("primary_cost_drivers", []),
        "risk_signals": profile.get("risk_signals", []),
        "implementation_note": "Production raw-material should-cost, TCO, risk, scoring, and decision workflow active in Build 0.9.4.",
    }
