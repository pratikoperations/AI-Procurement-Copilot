"""Intelligent RFQ engine regression tests."""

import pandas as pd

from modules.intelligent_rfq import detect_column_mapping, normalize_rfq_dataframe, normalize_units
from modules.validation import validate_rfq_dataframe


def test_header_aliases_map_to_canonical_columns():
    columns = ["Vendor Name", "Unit Rate", "Minimum Order Quantity", "Delivery Days", "Credit Terms", "Delivery Terms"]
    mapping, diagnostics = detect_column_mapping(columns)
    assert mapping["Vendor Name"] == "Supplier"
    assert mapping["Unit Rate"] == "Quoted Unit Price USD"
    assert mapping["Minimum Order Quantity"] == "MOQ"
    assert mapping["Delivery Days"] == "Lead Time Days"
    assert mapping["Credit Terms"] == "Payment Terms"
    assert mapping["Delivery Terms"] == "Incoterms"
    assert len(diagnostics) == len(columns)


def test_unit_normalization():
    result = normalize_units(pd.Series(["kgs", "tonnes", "pcs", "ltr", "unknown"])).tolist()
    assert result == ["kg", "MT", "piece", "liter", "unknown"]


def test_normalization_preserves_unmapped_columns_and_adds_report():
    raw = pd.DataFrame({
        "Vendor": ["A", "B"],
        "Price USD": [10, 11],
        "Min Order Qty": [100, 200],
        "Lead Time": [7, 9],
        "Payment Term": ["Net 30", "Net 45"],
        "Incoterm": ["DDP", "FOB"],
        "UOM": ["kgs", "kgs"],
        "Buyer Note": ["Preferred", "Backup"],
    })
    normalized, report = normalize_rfq_dataframe(raw)
    assert "Supplier" in normalized.columns
    assert "Quoted Unit Price USD" in normalized.columns
    assert "Buyer Note" in normalized.columns
    assert normalized["Unit"].tolist() == ["kg", "kg"]
    assert "Buyer Note" in report["unmapped_columns"]
    assert report["quality_score"] > 70


def test_duplicate_supplier_detection_and_quality_warning():
    raw = pd.DataFrame({
        "Supplier Name": ["A", "A"],
        "Quoted Price": [1.0, 1.1],
        "MOQ": [100, 100],
        "Lead Days": [10, 12],
        "Payment Terms": ["Net 30", "Net 30"],
        "Incoterms": ["DDP", "DDP"],
    })
    normalized, report = normalize_rfq_dataframe(raw)
    result = validate_rfq_dataframe(normalized)
    assert report["duplicate_supplier_rows"] == 2
    assert any("Duplicate supplier" in warning for warning in result["warnings"])


def test_missing_required_column_fails_after_mapping():
    raw = pd.DataFrame({
        "Vendor": ["A", "B"],
        "Unit Price": [1.0, 1.1],
    })
    normalized, _ = normalize_rfq_dataframe(raw)
    result = validate_rfq_dataframe(normalized)
    assert result["is_valid"] is False
    assert any("Missing required columns after intelligent mapping" in error for error in result["errors"])
