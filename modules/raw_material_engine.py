"""Raw-material category engine foundation.

Build 0.9.1 introduces the category contract and commodity metadata only.
The full raw-material should-cost, risk, and scoring logic is planned for Build 0.9.4.
"""

from modules.commodity_library import get_commodities, get_commodity_profile

CATEGORY_NAME = "Raw Material Procurement"
ENGINE_STATUS = "Foundation Preview"


def get_engine_profile(commodity=None):
    """Return raw-material engine metadata without claiming production scoring readiness."""
    commodities = get_commodities(CATEGORY_NAME)
    selected = commodity if commodity in commodities else commodities[0]
    profile = get_commodity_profile(CATEGORY_NAME, selected)
    return {
        "category": CATEGORY_NAME,
        "engine_status": ENGINE_STATUS,
        "selected_commodity": selected,
        "commodities": commodities,
        "cost_model": "Commodity Index + Conversion Premium + Delivered Cost + Risk-Adjusted TCO",
        "risk_model": "Volatility, supply concentration, import, FX, substitution, and continuity risk",
        "unit": profile.get("unit", "kg"),
        "primary_cost_drivers": profile.get("primary_cost_drivers", []),
        "risk_signals": profile.get("risk_signals", []),
        "implementation_note": (
            "Architecture and commodity metadata are active. Full raw-material scoring and "
            "should-cost execution will be implemented in Build 0.9.4."
        ),
    }
