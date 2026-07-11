"""Packaging category engine metadata and interfaces."""

from modules.commodity_library import get_commodities, get_commodity_profile

CATEGORY_NAME = "Packaging Procurement"
ENGINE_STATUS = "Active"


def get_engine_profile(commodity=None):
    """Return packaging engine metadata used by the category router and UI."""
    commodities = get_commodities(CATEGORY_NAME)
    selected = commodity if commodity in commodities else commodities[0]
    profile = get_commodity_profile(CATEGORY_NAME, selected)
    return {
        "category": CATEGORY_NAME,
        "engine_status": ENGINE_STATUS,
        "selected_commodity": selected,
        "commodities": commodities,
        "cost_model": "Packaging Should-Cost + Risk-Adjusted TCO",
        "risk_model": "Packaging supplier, quality, service, compliance, and continuity risk",
        "unit": profile.get("unit", "piece"),
        "primary_cost_drivers": profile.get("primary_cost_drivers", []),
        "risk_signals": profile.get("risk_signals", []),
        "implementation_note": "Current production engine for Portfolio Edition v1.0.",
    }
