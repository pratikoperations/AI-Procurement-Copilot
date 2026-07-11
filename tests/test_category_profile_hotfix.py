"""Regression tests for Build 0.9.3.1 category profile integration hotfix."""

from modules.category_engine import DEFAULT_CATEGORY_PROFILE, ensure_category_profile
from modules.sidebar import build_sidebar_result


def test_sidebar_contract_always_contains_category_profile():
    result = build_sidebar_result(category="Packaging Procurement")
    assert "category_profile" in result
    assert result["category_profile"]["category"] == "Packaging Procurement"
    assert result["category_profile"]["selected_commodity"]


def test_explicit_profile_is_preserved_and_completed():
    result = build_sidebar_result(
        category="Raw Material Procurement",
        category_profile={
            "category": "Raw Material Procurement",
            "selected_commodity": "PET Resin",
            "engine_status": "Foundation Preview",
            "commodities": ["PET Resin"],
            "unit": "kg",
            "cost_model": "Commodity Index + Delivered Cost",
            "risk_model": "Commodity and continuity risk",
            "primary_cost_drivers": ["commodity index"],
            "risk_signals": ["volatility"],
            "implementation_note": "Preview",
        },
    )
    profile = result["category_profile"]
    assert profile["category"] == "Raw Material Procurement"
    assert profile["selected_commodity"] == "PET Resin"
    assert profile["currency"] == "USD"
    assert profile["units"] == ["kg"]


def test_fallback_profile_is_reusable_and_complete():
    first = ensure_category_profile(None)
    second = ensure_category_profile({})
    assert first == second
    assert first is not DEFAULT_CATEGORY_PROFILE
    required = {
        "category",
        "category_name",
        "selected_commodity",
        "commodity_group",
        "unit",
        "units",
        "currency",
        "default_weightings",
        "default_assumptions",
    }
    assert required.issubset(first)
