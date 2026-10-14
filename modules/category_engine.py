"""Category engine router for procurement intelligence."""

from copy import deepcopy

from modules.packaging_engine import CATEGORY_NAME as PACKAGING_CATEGORY
from modules.packaging_engine import get_engine_profile as get_packaging_profile
from modules.raw_material_engine import CATEGORY_NAME as RAW_MATERIAL_CATEGORY
from modules.raw_material_engine import get_engine_profile as get_raw_material_profile
from modules.mro_engine import CATEGORY_NAME as MRO_CATEGORY
from modules.mro_engine import get_engine_profile as get_mro_profile
from modules.logistics_engine import CATEGORY_NAME as LOGISTICS_CATEGORY
from modules.logistics_engine import get_engine_profile as get_logistics_profile

CATEGORY_REGISTRY = {
    PACKAGING_CATEGORY: get_packaging_profile,
    RAW_MATERIAL_CATEGORY: get_raw_material_profile,
    MRO_CATEGORY: get_mro_profile,
    LOGISTICS_CATEGORY: get_logistics_profile,
}

PACKAGING_MATERIALS_CATEGORY = "Packaging Materials"
RAW_MATERIALS_CATEGORY = "Raw Materials"
INDIRECT_PROCUREMENT_CATEGORY = "Indirect Procurement"

TOP_LEVEL_PROCUREMENT_CATEGORIES = (
    PACKAGING_MATERIALS_CATEGORY,
    RAW_MATERIALS_CATEGORY,
    INDIRECT_PROCUREMENT_CATEGORY,
)

INDIRECT_PROCUREMENT_ENGINES = (
    MRO_CATEGORY,
    LOGISTICS_CATEGORY,
)

TOP_LEVEL_ENGINE_MAP = {
    PACKAGING_MATERIALS_CATEGORY: PACKAGING_CATEGORY,
    RAW_MATERIALS_CATEGORY: RAW_MATERIAL_CATEGORY,
}

DEFAULT_CATEGORY_PROFILE = {
    "category": PACKAGING_CATEGORY,
    "category_name": PACKAGING_CATEGORY,
    "engine_status": "Active",
    "selected_commodity": "Corrugated Board",
    "commodity_group": "Paper Packaging",
    "commodities": ["Corrugated Board"],
    "unit": "piece",
    "units": ["piece"],
    "currency": "USD",
    "cost_model": "Packaging Should-Cost + Risk-Adjusted TCO",
    "risk_model": "Packaging supplier, quality, service, compliance, and continuity risk",
    "primary_cost_drivers": ["kraft paper", "conversion", "printing", "freight"],
    "risk_signals": ["paper index volatility", "moisture", "compression strength", "MOQ"],
    "default_weightings": {
        "tco": 0.40,
        "risk": 0.20,
        "lead_time": 0.10,
        "payment": 0.08,
        "moq": 0.07,
        "performance": 0.10,
        "esg": 0.05,
    },
    "default_assumptions": {
        "annual_volume": 500000,
        "raw_material_shock": 0.0,
        "freight_shock": 0.0,
        "demand_change": 0.0,
    },
    "implementation_note": "Default packaging profile used as a safe application fallback.",
}


def get_supported_categories():
    """Return registered engine categories for backward-compatible routing."""
    return list(CATEGORY_REGISTRY.keys())


def get_supported_procurement_categories():
    """Return the three user-facing top-level procurement categories."""
    return list(TOP_LEVEL_PROCUREMENT_CATEGORIES)


def get_indirect_procurement_categories():
    """Return engine categories grouped under Indirect Procurement."""
    return list(INDIRECT_PROCUREMENT_ENGINES)


def resolve_category_engine(procurement_category, indirect_category=None):
    """Resolve a user-facing procurement taxonomy choice to an existing engine."""
    if procurement_category in TOP_LEVEL_ENGINE_MAP:
        if indirect_category not in (None, ""):
            raise ValueError(
                f"Indirect category is not applicable to '{procurement_category}'."
            )
        return TOP_LEVEL_ENGINE_MAP[procurement_category]

    if procurement_category == INDIRECT_PROCUREMENT_CATEGORY:
        if indirect_category not in INDIRECT_PROCUREMENT_ENGINES:
            supported = ", ".join(INDIRECT_PROCUREMENT_ENGINES)
            raise ValueError(
                "Indirect Procurement requires a valid indirect category. "
                f"Supported indirect categories: {supported}"
            )
        return indirect_category

    supported = ", ".join(TOP_LEVEL_PROCUREMENT_CATEGORIES)
    raise ValueError(
        f"Unsupported procurement category '{procurement_category}'. "
        f"Supported categories: {supported}"
    )


def get_procurement_category_for_engine(engine_category):
    """Return the user-facing parent category for an existing engine identifier."""
    if engine_category == PACKAGING_CATEGORY:
        return PACKAGING_MATERIALS_CATEGORY
    if engine_category == RAW_MATERIAL_CATEGORY:
        return RAW_MATERIALS_CATEGORY
    if engine_category in INDIRECT_PROCUREMENT_ENGINES:
        return INDIRECT_PROCUREMENT_CATEGORY
    raise ValueError(f"Unsupported engine category '{engine_category}'.")


def get_category_profile(category, commodity=None):
    """Route category requests to the correct engine profile."""
    try:
        resolver = CATEGORY_REGISTRY[category]
    except KeyError as exc:
        supported = ", ".join(get_supported_categories())
        raise ValueError(f"Unsupported category '{category}'. Supported categories: {supported}") from exc
    return resolver(commodity)


def ensure_category_profile(profile=None):
    """Return a complete profile while preserving all explicitly supplied values."""
    supplied = profile if isinstance(profile, dict) else {}
    result = deepcopy(DEFAULT_CATEGORY_PROFILE)
    result.update(supplied)

    result.setdefault("category_name", result.get("category", PACKAGING_CATEGORY))
    result.setdefault("commodity_group", "General Procurement")
    result.setdefault("currency", "USD")
    result.setdefault("default_weightings", deepcopy(DEFAULT_CATEGORY_PROFILE["default_weightings"]))
    result.setdefault("default_assumptions", deepcopy(DEFAULT_CATEGORY_PROFILE["default_assumptions"]))

    # Keep singular and plural unit fields consistent without allowing defaults
    # to override an explicitly supplied unit or units value.
    if "units" not in supplied and "unit" in supplied:
        result["units"] = [supplied["unit"]]
    elif "unit" not in supplied and "units" in supplied and supplied["units"]:
        result["unit"] = supplied["units"][0]
    else:
        result.setdefault("units", [result.get("unit", "piece")])

    return result


def is_production_ready(category):
    """Return whether the selected category has a production-ready scoring engine."""
    return get_category_profile(category)["engine_status"] == "Active"
