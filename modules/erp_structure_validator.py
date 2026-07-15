"""Structural validation for Version 1.1 ERP workbook summaries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from modules.erp_schema_registry import REQUIRED_SHEETS
from modules.erp_workbook_loader import SheetSummary, WorkbookSummary


PASS = "PASS"
PASS_WITH_WARNINGS = "PASS WITH WARNINGS"
BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class StructuralFinding:
    """One auditable structural validation finding."""

    code: str
    severity: str
    message: str
    sheet_name: str | None = None


@dataclass(frozen=True)
class SheetValidationSummary:
    """Validation result for one detected worksheet."""

    sheet_name: str
    status: str
    findings: tuple[StructuralFinding, ...]


@dataclass(frozen=True)
class WorkbookValidationSummary:
    """Workbook-level structural validation result."""

    status: str
    required_sheet_count: int
    detected_sheet_count: int
    missing_sheets: tuple[str, ...]
    unknown_sheets: tuple[str, ...]
    sheet_results: tuple[SheetValidationSummary, ...]
    findings: tuple[StructuralFinding, ...]

    @property
    def blocking_count(self) -> int:
        return sum(finding.severity == "BLOCKING" for finding in self.findings)

    @property
    def warning_count(self) -> int:
        return sum(finding.severity in {"WARNING", "INFO"} for finding in self.findings)


def _normalized_header(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def find_blank_headers(headers: Iterable[object]) -> tuple[int, ...]:
    """Return one-based positions of blank or whitespace-only headers."""

    return tuple(
        index
        for index, value in enumerate(headers, start=1)
        if not _normalized_header(value)
    )


def find_duplicate_headers(headers: Iterable[object]) -> tuple[str, ...]:
    """Return duplicate header labels using case-insensitive comparison."""

    seen: dict[str, str] = {}
    duplicates: list[str] = []
    for value in headers:
        label = _normalized_header(value)
        if not label:
            continue
        key = label.casefold()
        if key in seen:
            canonical_label = seen[key]
            if canonical_label not in duplicates:
                duplicates.append(canonical_label)
        else:
            seen[key] = label
    return tuple(duplicates)


def _validate_sheet(sheet: SheetSummary) -> SheetValidationSummary:
    findings: list[StructuralFinding] = []

    if sheet.is_empty:
        findings.append(
            StructuralFinding(
                code="EMPTY_REQUIRED_SHEET",
                severity="BLOCKING",
                sheet_name=sheet.name,
                message=f"Required sheet '{sheet.name}' contains no data rows.",
            )
        )

    blank_positions = find_blank_headers(sheet.headers)
    if blank_positions:
        positions = ", ".join(str(position) for position in blank_positions)
        findings.append(
            StructuralFinding(
                code="BLANK_HEADER",
                severity="BLOCKING",
                sheet_name=sheet.name,
                message=(
                    f"Sheet '{sheet.name}' contains blank header cells at columns: "
                    f"{positions}."
                ),
            )
        )

    duplicate_headers = find_duplicate_headers(sheet.headers)
    if duplicate_headers:
        labels = ", ".join(duplicate_headers)
        findings.append(
            StructuralFinding(
                code="DUPLICATE_HEADER",
                severity="BLOCKING",
                sheet_name=sheet.name,
                message=f"Sheet '{sheet.name}' contains duplicate headers: {labels}.",
            )
        )

    status = BLOCKED if any(item.severity == "BLOCKING" for item in findings) else PASS
    return SheetValidationSummary(
        sheet_name=sheet.name,
        status=status,
        findings=tuple(findings),
    )


def validate_workbook_structure(summary: WorkbookSummary) -> WorkbookValidationSummary:
    """Validate required sheets and structural header integrity.

    Unknown sheets are reported but do not block the workbook. Missing required
    sheets, empty required sheets, blank headers, and duplicate headers block it.
    """

    detected = tuple(summary.sheet_names)
    missing_sheets = tuple(sheet for sheet in REQUIRED_SHEETS if sheet not in summary.sheets)
    unknown_sheets = tuple(sheet for sheet in detected if sheet not in REQUIRED_SHEETS)

    workbook_findings: list[StructuralFinding] = []
    for sheet_name in missing_sheets:
        workbook_findings.append(
            StructuralFinding(
                code="MISSING_REQUIRED_SHEET",
                severity="BLOCKING",
                sheet_name=sheet_name,
                message=f"Required sheet '{sheet_name}' is missing.",
            )
        )

    for sheet_name in unknown_sheets:
        workbook_findings.append(
            StructuralFinding(
                code="UNKNOWN_SHEET",
                severity="INFO",
                sheet_name=sheet_name,
                message=f"Unknown sheet '{sheet_name}' was detected and logged.",
            )
        )

    sheet_results = tuple(
        _validate_sheet(summary.sheets[sheet_name])
        for sheet_name in REQUIRED_SHEETS
        if sheet_name in summary.sheets
    )
    for result in sheet_results:
        workbook_findings.extend(result.findings)

    if any(finding.severity == "BLOCKING" for finding in workbook_findings):
        status = BLOCKED
    elif workbook_findings:
        status = PASS_WITH_WARNINGS
    else:
        status = PASS

    return WorkbookValidationSummary(
        status=status,
        required_sheet_count=len(REQUIRED_SHEETS),
        detected_sheet_count=len(detected),
        missing_sheets=missing_sheets,
        unknown_sheets=unknown_sheets,
        sheet_results=sheet_results,
        findings=tuple(workbook_findings),
    )
