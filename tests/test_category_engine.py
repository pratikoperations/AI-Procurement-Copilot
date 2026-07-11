"""Category engine regression tests."""

import pytest

from modules.category_engine import (
    get_category_profile,
    get_supported_categories,
    is_production_ready,
)
from modules.commodity_library import get_commodities, get_commodity_profile


def test_supported_categories_include_packaging_and_raw_materials():
    categories = get_supported_categories()
    assert "Packaging Procurement" in categories
    assert "Raw Material Procurement" in categories


def test_packaging_engine_is_production_ready():
    profile = get_category_profile("Packaging Procurement", "Corrugated Board")
    assert profile["engine_status"] == "Active"
    assert profile["selected_commodity"] == "Corrugated Board"
    assert is_production_ready("Packaging Procurement") is True


def test_raw_material_engine_is_production_ready():
    profile = get_category_profile("Raw Material Procurement", "PET Resin")
    assert profile["engine_status"] == "Active"
    assert profile["selected_commodity"] == "PET Resin"
    assert is_production_ready("Raw Material Procurement") is True
    assert profile["unit"] == "kg"
    assert profile["cost_model"]
    assert profile["risk_model"]


def test_commodity_profiles_have_required_metadata():
    for category in get_supported_categories():
        commodities = get_commodities(category)
        assert commodities
        for commodity in commodities:
            profile = get_commodity_profile(category, commodity)
            assert profile["family"]
            assert profile["unit"]
            assert profile["primary_cost_drivers"]
            assert profile["risk_signals"]


def test_unsupported_category_fails_clearly():
    with pytest.raises(ValueError, match="Unsupported category"):
        get_category_profile("Unknown Category")
