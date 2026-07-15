import io

import pandas as pd

from modules.category_engine import get_category_profile
from modules.executive_outputs import generate_supplier_email
from modules.exports import build_excel_workbook, build_readable_allocation
from modules.sidebar import build_sidebar_result
from modules.unit_display import (
    add_annual_volume_metadata,
    annual_volume_label,
    display_unit,
    format_annual_volume,
    quantity_basis_caption,
)


def test_category_units_map_to_piece_or_kg():
    assert get_category_profile("Packaging Procurement", "Corrugated Board")["unit"] == "piece"
    assert get_category_profile("Packaging Procurement", "PET Bottles")["unit"] == "piece"
    assert get_category_profile("Packaging Procurement", "Labels")["unit"] == "piece"
    assert get_category_profile("Packaging Procurement", "Flexible Laminates")["unit"] == "kg"
    assert get_category_profile("Raw Material Procurement", "PET Resin")["unit"] == "kg"


def test_sidebar_result_includes_canonical_annual_volume_unit():
    result = build_sidebar_result(category_profile={"unit": "kg"}, annual_volume=500000)
    assert result["annual_volume_unit"] == "kg"


def test_dynamic_labels_and_quantity_captions():
    assert annual_volume_label("piece") == "Annual Volume (pieces)"
    assert annual_volume_label("kg") == "Annual Volume (kg)"
    assert format_annual_volume(500000, "piece") == "500,000 pieces"
    assert format_annual_volume(500000, "kg") == "500,000 kg"
    assert quantity_basis_caption(500000, "kg") == "Canonical quantity basis: 500,000 kg (500.000 metric tonnes)"


def test_supplier_email_pluralizes_piece_and_preserves_kg():
    supplier = {"Supplier": "A", "Quoted Unit Price USD": 2.0}
    pieces = generate_supplier_email(supplier, 1.8, 500000, unit="piece")
    kilograms = generate_supplier_email(supplier, 1.8, 500000, unit="kg")
    assert "500,000 pieces" in pieces
    assert "per pieces" in pieces
    assert "500,000 kg" in kilograms
    assert "per kg" in kilograms


def test_readable_allocation_adds_unit_metadata_without_mutating_source():
    source = pd.DataFrame([{"Supplier": "A", "Estimated Annual TCO USD": 1000.0}])
    original = source.copy(deep=True)
    report = build_readable_allocation(
        source,
        display_currency="USD",
        fx_rate=83,
        annual_volume=500000,
        annual_volume_unit="piece",
    )
    assert report.loc[0, "Annual Volume"] == 500000.0
    assert report.loc[0, "Annual Volume Unit"] == "piece"
    assert report.loc[0, "Quantity Basis"] == "500,000 pieces"
    pd.testing.assert_frame_equal(source, original)


def test_metadata_helper_is_backward_compatible():
    source = pd.DataFrame([{"A": 1}])
    result = add_annual_volume_metadata(source)
    pd.testing.assert_frame_equal(source, result)


def test_excel_readable_sheets_include_unit_metadata_and_audit_stays_canonical():
    scored = pd.DataFrame([{
        "Supplier": "A",
        "adjusted_tco_unit_usd": 1.0,
        "annual_tco_usd": 1000.0,
    }])
    should_cost = pd.DataFrame([{"Component": "Resin", "Unit Cost USD": 2.0}])
    allocation = pd.DataFrame([{"Supplier": "A", "Estimated Annual TCO USD": 1000.0}])
    scenarios = pd.DataFrame([{"Scenario": "Base", "Annual TCO (USD)": 1000.0}])
    workbook = build_excel_workbook(
        scored,
        should_cost,
        allocation,
        scenarios,
        display_currency="USD",
        fx_rate=83,
        annual_volume=500000,
        annual_volume_unit="kg",
    )
    sheets = pd.read_excel(io.BytesIO(workbook), sheet_name=None)
    for name in ["Supplier Scores Report", "Should Cost", "Allocation", "Scenarios"]:
        assert "Annual Volume Unit" in sheets[name].columns
        assert sheets[name].loc[0, "Annual Volume Unit"] == "kg"
    assert "annual_tco_usd" in sheets["Audit Supplier Scores"].columns
    assert "Annual Volume Unit" not in sheets["Audit Supplier Scores"].columns
