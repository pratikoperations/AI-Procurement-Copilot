"""Category engine router for procurement intelligence."""

from modules.packaging_engine import CATEGORY_NAME as PACKAGING_CATEGORY
from modules.packaging_engine import get_engine_profile as get_packaging_profile
from modules.raw_material_engine import CATEGORY_NAME as RAW_MATERIAL_CATEGORY
from modules.raw_material_engine import get_engine_profile as get_raw_material_profile

CATEGORY_REGISTRY = {
    PACKAGING_CATEGORY: get_packaging_profile,
    RAW_MATERIAL_CATEGORY: get_raw_material_profile,
}


def get_supported_categories():
    """Return registered procurement categories."""
    return list(CATEGORY_REGISTRY.keys())


def get_category_profile(category, commodity=None):
    """Route category requests to the correct engine profile."""
    try:
        resolver = CATEGORY_REGISTRY[category]
    except KeyError as exc:
        supported = ", ".join(get_supported_categories())
        raise ValueError(f"Unsupported category '{category}'. Supported categories: {supported}") from exc
    return resolver(commodity)


def is_production_ready(category):
    """Return whether the selected category has a production-ready scoring engine."""
    return get_category_profile(category)["engine_status"] == "Active"
