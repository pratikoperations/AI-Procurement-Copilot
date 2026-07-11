"""Synthetic real-world file validation tests for Build 0.9.6."""

from pathlib import Path

import pandas as pd

from modules.business_rule_validator import validate_business_rules
from modules.intelligent_rfq import normalize_rfq_dataframe
from modules.validation import validate_rfq_dataframe

ROOT = Path(__file__).resolve().parents[1] / "validation_data"


def _load(relative_path):
    return pd.read_csv(ROOT / relative_path)


def test_standard_packaging_file_loads_and_validates():
    raw = _load("packaging/packaging_standard.csv")
    normalized, report = normalize_rfq_dataframe(raw)
    normalized.attrs["rfq_quality_report"] = report
    result = validate_rfq_dataframe(normalized)
    assert len(normalized) == 3
    assert result["is_valid"] is True
    assert report["quality_score"] >= 70


def test_alternate_headers_are_mapped_and_original_extra_fields_preserved():
    raw = _load("packaging/packaging_alternate_headers.csv")
    normalized, report = normalize_rfq_dataframe(raw)
    assert "Supplier" in normalized.columns
    assert "Quoted Unit Price USD" in normalized.columns
    assert "MOQ" in normalized.columns
    assert "Lead Time Days" in normalized.columns
    assert "Payment Terms" in normalized.columns
    assert "Incoterms" in normalized.columns
    assert len(report["mapped_columns"]) >= 6


def test_invalid_file_is_rejected():
    raw = _load("packaging/packaging_invalid_values.csv")
    normalized, report = normalize_rfq_dataframe(raw)
    normalized.attrs["rfq_quality_report"] = report
    validation = validate_rfq_dataframe(normalized)
    rules = validate_business_rules(normalized, 500000)
    assert validation["is_valid"] is False or rules["status"] == "Fail"


def test_mixed_currency_file_is_blocked():
    df = _load("raw_material/raw_material_mixed_currency.csv")
    rules = validate_business_rules(df, 500000)
    assert any("Mixed currencies" in issue for issue in rules["blocking_issues"])


def test_duplicate_supplier_file_is_flagged():
    df = _load("edge_cases/duplicate_suppliers.csv")
    result = validate_rfq_dataframe(df)
    assert any("Duplicate supplier" in warning for warning in result["warnings"])


def test_large_file_loads_all_fifty_suppliers():
    df = _load("edge_cases/large_50_supplier_file.csv")
    assert len(df) == 50
    result = validate_business_rules(df, 50000)
    assert result["status"] in {"Pass", "Warning"}


def test_capacity_shortfall_is_detected():
    df = _load("edge_cases/capacity_shortfall.csv")
    result = validate_business_rules(df, 1000)
    assert any("below annual demand" in issue for issue in result["blocking_issues"])
