"""Focused assurance for governed Explorer currency presentation."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from modules.calculation_explorer_currency_ui import prepare_currency_result_presentation


def _pet_item():
    return {
        "unit": "USD/kg",
        "result": {
            "commodity_index": 1.05,
            "conversion_premium": 0.08,
            "freight": 0.05,
            "duty": 0.03,
            "quality_premium": 0.02,
            "supplier_margin": 0.04,
            "target_unit_cost_usd": 1.2700000000000002,
            "commodity": "PET Resin",
        },
    }


def test_inr_mode_converts_principal_and_monetary_components_only():
    item = _pet_item()
    original = deepcopy(item)

    prepared = prepare_currency_result_presentation(item, "INR", 83)

    assert prepared["principal"] == {
        "key": "target_unit_cost_usd",
        "label": "Target Unit Cost",
        "value": "105.41",
        "unit": "INR/kg",
    }
    rows = {row["Component"]: row for row in prepared["components"]}
    assert rows["Commodity Index"] == {"Component": "Commodity Index", "Value": "1.05", "Unit": "Index"}
    assert rows["Conversion Premium"] == {"Component": "Conversion Premium", "Value": "6.64", "Unit": "INR/kg"}
    assert rows["Freight"] == {"Component": "Freight", "Value": "4.15", "Unit": "INR/kg"}
    assert rows["Commodity"] == {"Component": "Commodity", "Value": "PET Resin", "Unit": ""}
    assert prepared["technical_payload"] is item["result"]
    assert item == original


def test_usd_mode_preserves_business_values_and_units():
    prepared = prepare_currency_result_presentation(_pet_item(), "USD", 83)

    assert prepared["principal"]["value"] == "1.27"
    assert prepared["principal"]["unit"] == "USD/kg"
    rows = {row["Component"]: row for row in prepared["components"]}
    assert rows["Freight"]["Value"] == "0.05"
    assert rows["Freight"]["Unit"] == "USD/kg"


def test_both_mode_discloses_usd_and_inr_without_mutating_canonical_payload():
    item = _pet_item()
    original_result = deepcopy(item["result"])

    prepared = prepare_currency_result_presentation(item, "Both", 83)

    assert prepared["principal"]["value"] == "USD 1.27 / INR 105.41"
    assert prepared["principal"]["unit"] == "USD/kg / INR/kg"
    assert prepared["technical_payload"] == original_result
    assert item["result"] == original_result


def test_empty_and_scalar_results_remain_supported():
    empty = prepare_currency_result_presentation({"result": None, "unit": "USD/kg"}, "INR", 83)
    scalar = prepare_currency_result_presentation({"result": 10.0, "unit": "USD/unit"}, "INR", 83)

    assert empty["status"] == "unavailable"
    assert scalar["principal"] == {"label": "Result", "value": "830.00", "unit": "INR/unit"}


def test_invalid_currency_and_fx_rate_fail_closed():
    with pytest.raises(ValueError):
        prepare_currency_result_presentation(_pet_item(), "EUR", 83)
    with pytest.raises(ValueError, match="positive"):
        prepare_currency_result_presentation(_pet_item(), "INR", 0)


def test_explorer_page_exposes_governed_currency_controls_and_new_renderer():
    source = Path("pages/8_Governed_Calculation_Explorer.py").read_text(encoding="utf-8")

    assert "Explorer Display Currency" in source
    assert "USD-INR FX Rate" in source
    assert "render_currency_aware_calculation_explorer" in source
    assert "authoritative_result=authoritative_output" in source
    assert "authoritative_output=authoritative_output" in source


def test_currency_wrapper_keeps_canonical_payload_expander_collapsed():
    source = Path("modules/calculation_explorer_currency_ui.py").read_text(encoding="utf-8")

    assert 'st.expander("Technical result payload — canonical USD", expanded=False)' in source
    assert "Canonical calculation, trace and reconciliation remain in USD" in source
