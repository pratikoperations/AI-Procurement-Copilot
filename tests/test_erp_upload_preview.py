from pathlib import Path

from modules.erp_mapping_profiles import MappingProfile
from modules.erp_structure_validator import (
    BLOCKED,
    PASS,
    StructuralFinding,
    WorkbookValidationSummary,
)
from modules.erp_upload_preview import (
    build_finding_rows,
    build_mapping_rows,
    build_processing_gate,
    build_sheet_inventory,
    build_workbook_metrics,
)
from modules.erp_workbook_loader import SheetSummary, WorkbookSummary


def _summary(*, include_unknown=False):
    sheets = {
        "Supplier_Master": SheetSummary(
            name="Supplier_Master",
            headers=("Supplier_ID", "Supplier_Name"),
            row_count=2,
            column_count=2,
            is_empty=False,
        )
    }
    sheet_names = ["Supplier_Master"]
    if include_unknown:
        sheets["Notes"] = SheetSummary(
            name="Notes",
            headers=("Comment",),
            row_count=1,
            column_count=1,
            is_empty=False,
        )
        sheet_names.append("Notes")
    return WorkbookSummary(
        filename="preview.xlsx",
        file_size_bytes=1024,
        sheet_names=tuple(sheet_names),
        sheets=sheets,
    )


def _validation(status=PASS, findings=()):
    return WorkbookValidationSummary(
        status=status,
        required_sheet_count=7,
        detected_sheet_count=1,
        missing_sheets=(),
        unknown_sheets=(),
        sheet_results=(),
        findings=tuple(findings),
    )


def test_workbook_metrics_and_inventory_expose_structure_only():
    summary = _summary(include_unknown=True)

    metrics = build_workbook_metrics(summary)
    inventory = build_sheet_inventory(summary)

    assert metrics == {
        "filename": "preview.xlsx",
        "file_size_bytes": 1024,
        "detected_sheet_count": 2,
        "required_sheet_count": 7,
        "unknown_sheet_count": 1,
    }
    assert inventory[0]["Classification"] == "Required"
    assert inventory[1]["Classification"] == "Unknown"
    assert inventory[0]["Headers"] == "Supplier_ID, Supplier_Name"
    assert set(inventory[0]) == {
        "Sheet", "Rows", "Columns", "Empty", "Classification", "Headers"
    }


def test_validation_findings_are_display_ready():
    finding = StructuralFinding(
        code="MISSING_REQUIRED_SHEET",
        severity="BLOCKING",
        message="Required sheet 'Receipts' is missing.",
        sheet_name="Receipts",
    )

    rows = build_finding_rows(_validation(status=BLOCKED, findings=(finding,)))

    assert rows == [{
        "Severity": "BLOCKING",
        "Code": "MISSING_REQUIRED_SHEET",
        "Sheet": "Receipts",
        "Finding": "Required sheet 'Receipts' is missing.",
    }]


def test_static_mapping_rows_are_display_only_and_deterministic():
    profile = MappingProfile(
        profile_id="TEST",
        profile_version="1.0",
        erp_family="Custom",
        erp_product="Test",
        status="Draft",
        sheet_mappings={
            "Supplier_Master": {"LIFNR": "Supplier_ID"},
            "RFQ_Quotes": {},
            "Purchase_Orders": {},
            "Receipts": {},
            "Supplier_Performance": {},
            "Material_Master": {},
            "Cost_Drivers": {},
        },
        source_path=Path("test.json"),
    )

    assert build_mapping_rows(profile) == [{
        "Sheet": "Supplier_Master",
        "Source field": "LIFNR",
        "Canonical field": "Supplier_ID",
    }]


def test_blocked_gate_suppresses_mapping_and_downstream_processing():
    gate = build_processing_gate(_validation(status=BLOCKED))

    assert gate["mapping_preview_allowed"] is False
    assert gate["further_processing_allowed"] is False
    assert gate["status"] == BLOCKED


def test_passing_gate_allows_preview_but_never_processing():
    gate = build_processing_gate(_validation(status=PASS))

    assert gate["mapping_preview_allowed"] is True
    assert gate["further_processing_allowed"] is False
    assert gate["status"] == PASS
