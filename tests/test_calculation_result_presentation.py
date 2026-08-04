"""Focused assurance for business-readable Governed Calculation Explorer results."""
from __future__ import annotations

from pathlib import Path

from modules.calculation_explorer_ui import _prepare_result_presentation


def test_mapping_result_identifies_target_unit_cost_and_components():
    item = {
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

    prepared = _prepare_result_presentation(item)

    assert prepared["status"] == "mapping"
    assert prepared["principal"] == {
        "key": "target_unit_cost_usd",
        "label": "Target Unit Cost",
        "value": "1.27",
        "unit": "USD/kg",
    }
    component_names = {row["Component"] for row in prepared["components"]}
    assert component_names == {
        "Commodity Index",
        "Conversion Premium",
        "Freight",
        "Duty",
        "Quality Premium",
        "Supplier Margin",
        "Commodity",
    }
    assert prepared["technical_payload"] is item["result"]


def test_explicit_principal_result_identification_takes_precedence():
    prepared = _prepare_result_presentation({
        "unit": "INR/unit",
        "principal_result_key": "governed_total",
        "result": {"subtotal": 90.0, "governed_total": 100.0},
    })

    assert prepared["principal"]["key"] == "governed_total"
    assert prepared["principal"]["label"] == "Governed Total"
    assert prepared["principal"]["value"] == "100.00"


def test_nested_mapping_components_are_presented_as_rows_not_python_syntax():
    prepared = _prepare_result_presentation({
        "unit": "USD/unit",
        "result": {
            "components": {"paper": 1.0, "conversion": 0.2},
            "target_unit_cost_usd": 1.2,
        },
    })

    assert prepared["status"] == "mapping"
    assert prepared["principal"]["value"] == "1.2"
    assert prepared["components"] == [
        {"Component": "Paper", "Value": "1", "Unit": "USD/unit"},
        {"Component": "Conversion", "Value": "0.2", "Unit": "USD/unit"},
    ]


def test_scalar_result_is_presented_as_a_readable_metric():
    prepared = _prepare_result_presentation({"result": 478.0, "unit": "INR/hour"})

    assert prepared == {
        "status": "scalar",
        "principal": {"label": "Result", "value": "478.00", "unit": "INR/hour"},
        "components": [],
        "technical_payload": 478.0,
    }


def test_empty_result_fails_closed_without_fabricating_value():
    assert _prepare_result_presentation({"result": None, "unit": "USD/kg"}) == {
        "status": "unavailable",
        "technical_payload": None,
    }
    assert _prepare_result_presentation({"result": {}, "unit": "USD/kg"}) == {
        "status": "unavailable",
        "technical_payload": {},
    }


def test_overview_uses_technical_payload_expander_and_removes_raw_result_write():
    source = Path("modules/calculation_explorer_ui.py").read_text(encoding="utf-8")

    assert 'st.expander("Technical result payload", expanded=False)' in source
    assert "_render_result(item)" in source
    assert 'st.write(f"**Result:** `{item.get(\'result\')}`")' not in source
    assert "No value has been fabricated" in source


def test_existing_explorer_sections_remain_available():
    source = Path("modules/calculation_explorer_ui.py").read_text(encoding="utf-8")

    for section in ("Overview", "Assumptions", "Calculation Trace", "Reconciliation", "SourceMate", "Human Review"):
        assert section in source
