"""Procurement taxonomy reconciliation regression tests."""

from pathlib import Path

import pytest

from modules.category_engine import (
    INDIRECT_PROCUREMENT_CATEGORY,
    LOGISTICS_CATEGORY,
    MRO_CATEGORY,
    PACKAGING_CATEGORY,
    PACKAGING_MATERIALS_CATEGORY,
    RAW_MATERIAL_CATEGORY,
    RAW_MATERIALS_CATEGORY,
    get_indirect_procurement_categories,
    get_procurement_category_for_engine,
    get_supported_categories,
    get_supported_procurement_categories,
    resolve_category_engine,
)
from modules.config import DEFAULT_CATEGORY, SUPPORTED_CATEGORIES


def test_user_facing_taxonomy_has_exactly_three_top_level_categories():
    assert get_supported_procurement_categories() == [
        "Packaging Materials",
        "Raw Materials",
        "Indirect Procurement",
    ]
    assert SUPPORTED_CATEGORIES == [
        "Packaging Materials",
        "Raw Materials",
        "Indirect Procurement",
    ]
    assert DEFAULT_CATEGORY == "Packaging Materials"


def test_existing_engine_registry_remains_backward_compatible():
    assert PACKAGING_CATEGORY in get_supported_categories()
    assert RAW_MATERIAL_CATEGORY in get_supported_categories()
    assert MRO_CATEGORY in get_supported_categories()
    assert LOGISTICS_CATEGORY in get_supported_categories()


def test_direct_taxonomy_categories_resolve_to_existing_engines():
    assert resolve_category_engine(PACKAGING_MATERIALS_CATEGORY) == PACKAGING_CATEGORY
    assert resolve_category_engine(RAW_MATERIALS_CATEGORY) == RAW_MATERIAL_CATEGORY
    assert get_procurement_category_for_engine(PACKAGING_CATEGORY) == PACKAGING_MATERIALS_CATEGORY
    assert get_procurement_category_for_engine(RAW_MATERIAL_CATEGORY) == RAW_MATERIALS_CATEGORY


def test_mro_and_logistics_are_children_of_indirect_procurement():
    assert INDIRECT_PROCUREMENT_CATEGORY == "Indirect Procurement"
    assert get_indirect_procurement_categories() == [
        MRO_CATEGORY,
        LOGISTICS_CATEGORY,
    ]
    assert resolve_category_engine(INDIRECT_PROCUREMENT_CATEGORY, MRO_CATEGORY) == MRO_CATEGORY
    assert resolve_category_engine(INDIRECT_PROCUREMENT_CATEGORY, LOGISTICS_CATEGORY) == LOGISTICS_CATEGORY
    assert get_procurement_category_for_engine(MRO_CATEGORY) == INDIRECT_PROCUREMENT_CATEGORY
    assert get_procurement_category_for_engine(LOGISTICS_CATEGORY) == INDIRECT_PROCUREMENT_CATEGORY


def test_taxonomy_resolution_fails_closed_for_invalid_combinations():
    with pytest.raises(ValueError):
        resolve_category_engine(INDIRECT_PROCUREMENT_CATEGORY)
    with pytest.raises(ValueError):
        resolve_category_engine(INDIRECT_PROCUREMENT_CATEGORY, "Facilities")
    with pytest.raises(ValueError):
        resolve_category_engine(PACKAGING_MATERIALS_CATEGORY, MRO_CATEGORY)
    with pytest.raises(ValueError):
        resolve_category_engine("Unknown Category")


def test_sidebar_presents_hierarchy_but_preserves_engine_category_contract():
    source = Path("modules/sidebar.py").read_text(encoding="utf-8")
    assert 'st.sidebar.selectbox(\n        "Procurement Category"' in source
    assert '"Indirect Category"' in source
    assert '"Commodity / Service"' in source
    assert "resolve_category_engine(procurement_category, indirect_category)" in source
    assert "procurement_category=procurement_category" in source
    assert "indirect_category=indirect_category" in source
    assert "category=category" in source
