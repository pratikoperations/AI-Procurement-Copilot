"""Display-only helpers for the governed ERP upload preview.

This module converts existing immutable ERP foundation results into presentation
rows. It does not load files, transform records, persist data, or call any
procurement decision engine.
"""

from __future__ import annotations

from typing import Mapping

from modules.erp_mapping_profiles import MappingProfile
from modules.erp_schema_registry import REQUIRED_SHEETS
from modules.erp_structure_validator import BLOCKED, WorkbookValidationSummary
from modules.erp_workbook_loader import WorkbookSummary

STATUS_MESSAGES: Mapping[str, str] = {
    "PASS": "All defined structural checks passed. This does not confirm business-data accuracy or analysis readiness.",
    "PASS WITH WARNINGS": "Blocking structural checks passed, but non-blocking findings require human review.",
    "BLOCKED": "The workbook cannot proceed because blocking structural defects were found.",
}


def build_workbook_metrics(summary: WorkbookSummary) -> dict[str, object]:
    """Return display-safe workbook metrics without business-row values."""

    unknown_count = sum(name not in REQUIRED_SHEETS for name in summary.sheet_names)
    return {
        "filename": summary.filename,
        "file_size_bytes": summary.file_size_bytes,
        "detected_sheet_count": len(summary.sheet_names),
        "required_sheet_count": len(REQUIRED_SHEETS),
        "unknown_sheet_count": unknown_count,
    }


def build_sheet_inventory(summary: WorkbookSummary) -> list[dict[str, object]]:
    """Return deterministic sheet metadata rows; never include workbook data rows."""

    inventory: list[dict[str, object]] = []
    for sheet_name in summary.sheet_names:
        sheet = summary.sheets[sheet_name]
        inventory.append(
            {
                "Sheet": sheet.name,
                "Rows": sheet.row_count,
                "Columns": sheet.column_count,
                "Empty": "Yes" if sheet.is_empty else "No",
                "Classification": "Required" if sheet.name in REQUIRED_SHEETS else "Unknown",
                "Headers": ", ".join(str(value) for value in sheet.headers),
            }
        )
    return inventory


def build_finding_rows(validation: WorkbookValidationSummary) -> list[dict[str, str]]:
    """Return deterministic structural-finding rows for presentation."""

    return [
        {
            "Severity": finding.severity,
            "Code": finding.code,
            "Sheet": finding.sheet_name or "Workbook",
            "Finding": finding.message,
        }
        for finding in validation.findings
    ]


def build_mapping_rows(profile: MappingProfile) -> list[dict[str, str]]:
    """Flatten one static draft profile for display only."""

    rows: list[dict[str, str]] = []
    for sheet_name in REQUIRED_SHEETS:
        for source, target in profile.mapping_for(sheet_name).items():
            rows.append(
                {
                    "Sheet": sheet_name,
                    "Source field": source,
                    "Canonical field": target,
                }
            )
    return rows


def build_processing_gate(validation: WorkbookValidationSummary) -> dict[str, object]:
    """Return the immutable phase boundary for downstream behaviour."""

    return {
        "status": validation.status,
        "status_message": STATUS_MESSAGES[validation.status],
        "mapping_preview_allowed": validation.status != BLOCKED,
        "further_processing_allowed": False,
    }
