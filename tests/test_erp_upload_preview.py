from pathlib import Path

from modules.erp_mapping_profiles import load_default_mapping_profiles
from modules.erp_structure_validator import BLOCKED, validate_workbook_structure
from modules.erp_upload_preview import (
    build_finding_rows,
    build_mapping_rows,
    build_processing_gate,
    build_sheet_inventory,
    build_workbook_metrics,
)
from modules.erp_workbook_loader import load_erp_workbook

SAMPLE_DIR = Path("data/erp_samples")


def test_workbook_metrics_and_sheet_inventory_expose_structure_only():
    summary = load_erp_workbook(SAMPLE_DIR / "synthetic_sap_procurement_workbook.xlsx")

    metrics = build_workbook_metrics(summary)
    inventory = build_sheet_inventory(summary)

    assert metrics["filename"] == "synthetic_sap_procurement_workbook.xlsx"
    assert metrics["detected_sheet_count"] == len(summary.sheet_names)
    assert metrics["required_sheet_count"] == 7
    assert set(inventory[0]) == {
        "Sheet", "Rows", "Columns", "Empty", "Classification", "Headers"
    }
    assert "data" not in {key.lower() for row in inventory for key in row}


def test_unknown_sheet_is_classified_and_findings_are_display_ready():
    summary = load_erp_workbook(SAMPLE_DIR / "erp_adversarial_procurement_workbook.xlsx")
    validation = validate_workbook_structure(summary)

    inventory = build_sheet_inventory(summary)
    finding_rows = build_finding_rows(validation)

    assert any(row["Classification"] == "Unknown" for row in inventory)
    assert all(set(row) == {"Severity", "Code", "Sheet", "Finding"} for row in finding_rows)


def test_static_mapping_rows_are_display_only_and_deterministic():
    profile = load_default_mapping_profiles()["SAP_S4HANA"]

    rows = build_mapping_rows(profile)

    assert rows
    assert rows[0]["Sheet"] == "Supplier_Master"
    assert set(rows[0]) == {"Sheet", "Source field", "Canonical field"}


def test_blocked_gate_suppresses_mapping_and_all_downstream_processing():
    summary = load_erp_workbook(SAMPLE_DIR / "erp_adversarial_procurement_workbook.xlsx")
    validation = validate_workbook_structure(summary)
    gate = build_processing_gate(validation)

    assert validation.status == BLOCKED
    assert gate["mapping_preview_allowed"] is False
    assert gate["further_processing_allowed"] is False


def test_passing_gate_never_allows_downstream_processing():
    summary = load_erp_workbook(SAMPLE_DIR / "synthetic_oracle_procurement_workbook.xlsx")
    validation = validate_workbook_structure(summary)
    gate = build_processing_gate(validation)

    assert gate["mapping_preview_allowed"] is True
    assert gate["further_processing_allowed"] is False
