"""Governed v1.3 three-sheet RFQ workbook adapter.

This module is intentionally isolated from procurement, scoring, TCO and UI
engines. It converts a safely accepted XLSX workbook into typed canonical
records, mapping-review evidence, provenance and adapter-level findings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import re
from typing import Any, BinaryIO, Iterable, Mapping, Sequence

from openpyxl import load_workbook

from modules.erp_workbook_loader import (
    DEFAULT_MAX_FILE_SIZE_BYTES,
    WorkbookLoadError,
    load_erp_workbook,
)


CONTRACT_ROOT = Path(__file__).resolve().parents[1] / "planning" / "v1.3" / "build_group_b"
DEFAULT_SCHEMA_PATH = CONTRACT_ROOT / "minimum_workbook_schema_v1.3.0.json"
DEFAULT_ALIAS_PATH = CONTRACT_ROOT / "sap_report_alias_registry_v1.3.0.json"
APPROVED_SHEETS = ("RFQ_QUOTES", "PO_HISTORY", "UPLOAD_METADATA")
HIGH_RISK_FIELDS = {
    "SOURCING_EVENT_ID", "RFQ_NUMBER", "RFQ_ITEM", "SUPPLIER_ID",
    "QUOTATION_VERSION", "REQUESTED_QUANTITY", "QUOTED_QUANTITY",
    "ORDER_QUANTITY", "BASE_UNIT_PRICE", "NET_PRICE", "PRICE_UNIT",
    "CURRENCY", "QUOTATION_UOM", "ORDER_UOM", "COMPARISON_UOM",
    "UOM_CONVERSION_FACTOR", "EXCHANGE_RATE", "EXCHANGE_RATE_DATE",
}
FORMULA_HIGH_RISK_FIELDS = HIGH_RISK_FIELDS | {
    "QUOTATION_DATE", "VALIDITY_END_DATE", "QUOTATION_STATUS", "PO_DATE",
    "PO_STATUS", "PO_NUMBER", "PO_ITEM", "SOURCE_ROW_ID",
}


@dataclass(frozen=True)
class ValidationFinding:
    severity: str
    code: str
    message: str
    sheet: str | None = None
    row_number: int | None = None
    field_name: str | None = None


@dataclass(frozen=True)
class MappingReview:
    sheet: str
    source_header: str
    canonical_field: str | None
    confidence_class: str
    source_classification: str | None
    requires_confirmation: bool
    reason: str | None = None


@dataclass(frozen=True)
class SourceProvenance:
    source_filename: str
    sheet: str
    source_row_number: int
    source_row_id: str
    source_file_hash_sha256: str | None
    upload_file_hash_sha256: str
    alias_registry_version: str
    schema_version: str


@dataclass(frozen=True)
class CanonicalRecord:
    sheet: str
    original_values: Mapping[str, Any]
    canonical_values: Mapping[str, Any]
    normalized_values: Mapping[str, Any]
    provenance: SourceProvenance
    active: bool = True


@dataclass(frozen=True)
class WorkbookAdapterResult:
    filename: str
    upload_file_hash_sha256: str
    mode: str
    schema_version: str
    alias_registry_version: str
    selected_sourcing_event_id: str | None
    available_sourcing_event_ids: tuple[str, ...]
    rfq_quotes: tuple[CanonicalRecord, ...]
    po_history: tuple[CanonicalRecord, ...]
    upload_metadata: Mapping[str, Any] | None
    mapping_reviews: tuple[MappingReview, ...]
    findings: tuple[ValidationFinding, ...]

    @property
    def has_fatal(self) -> bool:
        return any(f.severity == "Fatal" for f in self.findings)

    @property
    def has_blocking(self) -> bool:
        return any(f.severity == "Blocking" for f in self.findings)


class WorkbookAdapterError(ValueError):
    """Raised when the adapter cannot safely produce a contract result."""


@dataclass
class _FindingCollector:
    findings: list[ValidationFinding] = field(default_factory=list)

    def add(
        self,
        severity: str,
        code: str,
        message: str,
        *,
        sheet: str | None = None,
        row_number: int | None = None,
        field_name: str | None = None,
    ) -> None:
        self.findings.append(
            ValidationFinding(severity, code, message, sheet, row_number, field_name)
        )


def _read_source_bytes(source: str | Path | bytes | bytearray | BinaryIO) -> bytes:
    if isinstance(source, (str, Path)):
        return Path(source).read_bytes()
    if isinstance(source, (bytes, bytearray)):
        return bytes(source)
    read = getattr(source, "read", None)
    if not callable(read):
        raise WorkbookAdapterError("Workbook source must be a path, bytes, or binary file object.")
    position = None
    try:
        if callable(getattr(source, "tell", None)):
            position = source.tell()
        if callable(getattr(source, "seek", None)):
            source.seek(0)
        payload = read()
    finally:
        if position is not None and callable(getattr(source, "seek", None)):
            source.seek(position)
    if not isinstance(payload, (bytes, bytearray)):
        raise WorkbookAdapterError("Workbook file object must return binary bytes.")
    return bytes(payload)


def _load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WorkbookAdapterError(f"Contract file could not be loaded: {path}") from exc


def _normalise_header(value: Any) -> str:
    text = "" if value is None else str(value).strip()
    text = re.sub(r"[\s\W_]+", " ", text, flags=re.UNICODE)
    return text.casefold().strip()


def _build_alias_index(registry: Mapping[str, Any], sheet: str) -> dict[str, list[str]]:
    index: dict[str, list[str]] = {}
    for canonical, aliases in registry.get("sheets", {}).get(sheet, {}).items():
        for alias in [canonical, *aliases]:
            index.setdefault(_normalise_header(alias), []).append(canonical)
    return index


def _map_headers(
    sheet: str,
    headers: Sequence[Any],
    registry: Mapping[str, Any],
    collector: _FindingCollector,
) -> tuple[dict[int, str], list[MappingReview]]:
    alias_index = _build_alias_index(registry, sheet)
    source_classes = registry.get("field_source_classifications", {}).get(sheet, {})
    mapped: dict[int, str] = {}
    reviews: list[MappingReview] = []
    targets: dict[str, int] = {}

    for idx, raw_header in enumerate(headers):
        source_header = "" if raw_header is None else str(raw_header).strip()
        normalized = _normalise_header(raw_header)
        candidates = alias_index.get(normalized, [])
        unique = tuple(dict.fromkeys(candidates))

        if not source_header:
            reviews.append(MappingReview(sheet, source_header, None, "UNMAPPED", None, False, "Blank header"))
            continue
        if len(unique) > 1:
            reviews.append(MappingReview(sheet, source_header, None, "AMBIGUOUS", None, True, f"Matches {unique}"))
            collector.add("Fatal", "AMBIGUOUS_HEADER_MAPPING", f"Header '{source_header}' maps to multiple canonical fields.", sheet=sheet)
            continue
        if not unique:
            reviews.append(MappingReview(sheet, source_header, None, "UNMAPPED", None, False, "No approved alias"))
            collector.add("Information", "UNMAPPED_SOURCE_COLUMN", f"Unmapped source column '{source_header}' is retained only in diagnostics.", sheet=sheet)
            continue

        canonical = unique[0]
        if canonical in targets:
            reviews.append(MappingReview(sheet, source_header, canonical, "AMBIGUOUS", source_classes.get(canonical), True, "Duplicate canonical target"))
            collector.add("Fatal", "DUPLICATE_CANONICAL_TARGET", f"Multiple source columns map to '{canonical}'.", sheet=sheet, field_name=canonical)
            continue

        exact = source_header.casefold() in {
            str(alias).strip().casefold()
            for alias in [canonical, *registry.get("sheets", {}).get(sheet, {}).get(canonical, [])]
        }
        confidence = "EXACT_APPROVED" if exact else "NORMALIZED_APPROVED"
        requires_confirmation = canonical in HIGH_RISK_FIELDS and confidence != "EXACT_APPROVED"
        reviews.append(
            MappingReview(
                sheet,
                source_header,
                canonical,
                confidence,
                source_classes.get(canonical),
                requires_confirmation,
                "High-risk normalized mapping requires confirmation" if requires_confirmation else None,
            )
        )
        mapped[idx] = canonical
        targets[canonical] = idx
        if requires_confirmation:
            collector.add("Blocking", "HIGH_RISK_MAPPING_CONFIRMATION_REQUIRED", f"Mapping '{source_header}' to '{canonical}' requires explicit confirmation.", sheet=sheet, field_name=canonical)

    return mapped, reviews


def _coerce_value(value: Any, schema: Mapping[str, Any], *, field_name: str) -> Any:
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    reference = schema.get("$ref")
    type_name = reference.rsplit("/", 1)[-1] if reference else schema.get("type")
    if type_name == "string":
        return str(value).strip()
    if type_name == "integer":
        if isinstance(value, bool):
            raise ValueError("boolean is not an integer")
        number = Decimal(str(value))
        if number != number.to_integral_value():
            raise ValueError("must be a whole number")
        return int(number)
    if type_name == "number":
        if isinstance(value, bool):
            raise ValueError("boolean is not numeric")
        return Decimal(str(value))
    if type_name == "boolean":
        if isinstance(value, bool):
            return value
        normalized = str(value).strip().casefold()
        if normalized in {"true", "yes", "y", "1", "x"}:
            return True
        if normalized in {"false", "no", "n", "0", ""}:
            return False
        raise ValueError("must be a recognised boolean")
    if type_name == "date":
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        return date.fromisoformat(str(value).strip())
    if type_name == "datetime":
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time())
        return datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    return value


def _resolve_filename(source: object, filename: str | None) -> str:
    if filename:
        return Path(filename).name
    if isinstance(source, (str, Path)):
        return Path(source).name
    source_name = getattr(source, "name", None)
    if source_name:
        return Path(str(source_name)).name
    return "PROCUREMENT_COPILOT_UPLOAD.xlsx"


def _row_is_empty(values: Iterable[Any]) -> bool:
    return all(value is None or (isinstance(value, str) and not value.strip()) for value in values)


def _formula_fields(row_cells: Sequence[Any], mapped_headers: Mapping[int, str]) -> list[str]:
    result: list[str] = []
    for idx, cell in enumerate(row_cells):
        if getattr(cell, "data_type", None) == "f" and idx in mapped_headers:
            result.append(mapped_headers[idx])
    return result


def _parse_sheet(
    workbook: Any,
    sheet: str,
    filename: str,
    upload_hash: str,
    source_hash: str | None,
    schema_doc: Mapping[str, Any],
    registry: Mapping[str, Any],
    collector: _FindingCollector,
    confirmed_mappings: set[tuple[str, str, str]],
) -> tuple[list[CanonicalRecord], list[MappingReview]]:
    if sheet not in workbook.sheetnames:
        return [], []
    worksheet = workbook[sheet]
    rows = worksheet.iter_rows()
    header_cells = next(rows, None)
    if not header_cells:
        collector.add("Fatal", "EMPTY_SHEET", f"Sheet '{sheet}' has no header row.", sheet=sheet)
        return [], []

    headers = [cell.value for cell in header_cells]
    mapped_headers, reviews = _map_headers(sheet, headers, registry, collector)
    for review in reviews:
        if review.requires_confirmation and review.canonical_field is not None:
            key = (sheet, review.source_header, review.canonical_field)
            if key in confirmed_mappings:
                collector.findings[:] = [
                    f for f in collector.findings
                    if not (
                        f.code == "HIGH_RISK_MAPPING_CONFIRMATION_REQUIRED"
                        and f.sheet == sheet
                        and f.field_name == review.canonical_field
                    )
                ]

    def_name = {"RFQ_QUOTES": "RFQQuoteRow", "PO_HISTORY": "POHistoryRow", "UPLOAD_METADATA": "UploadMetadataRow"}[sheet]
    row_schema = schema_doc["$defs"][def_name]
    required = set(row_schema.get("required", []))
    mapped_fields = set(mapped_headers.values())
    missing_headers = sorted(required - mapped_fields)
    for field_name in missing_headers:
        collector.add("Fatal", "MANDATORY_HEADER_MISSING", f"Mandatory field '{field_name}' is not mapped.", sheet=sheet, field_name=field_name)

    records: list[CanonicalRecord] = []
    for row_number, row_cells in enumerate(rows, start=2):
        values = [cell.value for cell in row_cells]
        if _row_is_empty(values):
            continue
        formula_fields = _formula_fields(row_cells, mapped_headers)
        for field_name in formula_fields:
            severity = "Blocking" if field_name in FORMULA_HIGH_RISK_FIELDS else "Warning"
            collector.add(severity, "FORMULA_CELL_REJECTED", f"Formula cell is not accepted for '{field_name}'.", sheet=sheet, row_number=row_number, field_name=field_name)

        original: dict[str, Any] = {}
        canonical: dict[str, Any] = {}
        for idx, value in enumerate(values):
            source_header = headers[idx] if idx < len(headers) else f"COLUMN_{idx + 1}"
            original[str(source_header)] = value
            canonical_name = mapped_headers.get(idx)
            if canonical_name is None or canonical_name in formula_fields:
                continue
            property_schema = row_schema.get("properties", {}).get(canonical_name, {})
            try:
                canonical[canonical_name] = _coerce_value(value, property_schema, field_name=canonical_name)
            except (ValueError, TypeError, InvalidOperation) as exc:
                collector.add("Fatal" if canonical_name in required else "Blocking", "VALUE_TYPE_INVALID", f"Invalid value for '{canonical_name}': {exc}", sheet=sheet, row_number=row_number, field_name=canonical_name)
                canonical[canonical_name] = None

        for field_name in required:
            if canonical.get(field_name) is None:
                collector.add("Fatal", "MANDATORY_VALUE_MISSING", f"Mandatory value '{field_name}' is missing.", sheet=sheet, row_number=row_number, field_name=field_name)

        source_row_id = str(canonical.get("SOURCE_ROW_ID") or f"{sheet}:{row_number}")
        provenance = SourceProvenance(
            source_filename=filename,
            sheet=sheet,
            source_row_number=row_number,
            source_row_id=source_row_id,
            source_file_hash_sha256=source_hash,
            upload_file_hash_sha256=upload_hash,
            alias_registry_version=str(registry.get("registry_version", "unknown")),
            schema_version=str(schema_doc.get("version", "unknown")),
        )
        records.append(
            CanonicalRecord(
                sheet=sheet,
                original_values=original,
                canonical_values=canonical,
                normalized_values={},
                provenance=provenance,
            )
        )
    return records, reviews


def _validate_positive_fields(records: Sequence[CanonicalRecord], collector: _FindingCollector) -> None:
    positive_fields = {"REQUESTED_QUANTITY", "QUOTED_QUANTITY", "ORDER_QUANTITY", "PRICE_UNIT", "UOM_CONVERSION_FACTOR", "EXCHANGE_RATE"}
    non_negative_fields = {"BASE_UNIT_PRICE", "NET_PRICE", "NET_ORDER_VALUE"}
    for record in records:
        row_number = record.provenance.source_row_number
        for field_name in positive_fields:
            value = record.canonical_values.get(field_name)
            if value is not None and value <= 0:
                collector.add("Blocking", "POSITIVE_VALUE_REQUIRED", f"'{field_name}' must be greater than zero.", sheet=record.sheet, row_number=row_number, field_name=field_name)
        for field_name in non_negative_fields:
            value = record.canonical_values.get(field_name)
            if value is not None and value < 0:
                collector.add("Blocking", "NEGATIVE_VALUE_REJECTED", f"'{field_name}' cannot be negative.", sheet=record.sheet, row_number=row_number, field_name=field_name)


def _validate_composite_keys(records: Sequence[CanonicalRecord], collector: _FindingCollector) -> None:
    key_fields_by_sheet = {
        "RFQ_QUOTES": ("SOURCING_EVENT_ID", "RFQ_NUMBER", "RFQ_ITEM", "SUPPLIER_ID", "QUOTATION_VERSION"),
        "PO_HISTORY": ("PO_NUMBER", "PO_ITEM"),
    }
    seen: dict[tuple[str, tuple[Any, ...]], Mapping[str, Any]] = {}
    for record in records:
        key_fields = key_fields_by_sheet.get(record.sheet)
        if not key_fields:
            continue
        key = tuple(record.canonical_values.get(name) for name in key_fields)
        compound = (record.sheet, key)
        prior = seen.get(compound)
        if prior is None:
            seen[compound] = record.canonical_values
        elif dict(prior) != dict(record.canonical_values):
            collector.add("Fatal", "CONTRADICTORY_DUPLICATE_KEY", f"Contradictory duplicate key {key}.", sheet=record.sheet, row_number=record.provenance.source_row_number)
        else:
            collector.add("Warning", "EXACT_DUPLICATE_ROW", f"Exact duplicate key {key}.", sheet=record.sheet, row_number=record.provenance.source_row_number)


def _activate_latest_versions(records: Sequence[CanonicalRecord], collector: _FindingCollector) -> list[CanonicalRecord]:
    grouped: dict[tuple[Any, ...], list[CanonicalRecord]] = {}
    for record in records:
        values = record.canonical_values
        group_key = (values.get("SOURCING_EVENT_ID"), values.get("RFQ_NUMBER"), values.get("RFQ_ITEM"), values.get("SUPPLIER_ID"))
        grouped.setdefault(group_key, []).append(record)

    result: list[CanonicalRecord] = []
    for group in grouped.values():
        versions = [r.canonical_values.get("QUOTATION_VERSION") for r in group]
        valid_versions = [v for v in versions if isinstance(v, int)]
        if not valid_versions:
            result.extend(group)
            continue
        highest = max(valid_versions)
        highest_records = [r for r in group if r.canonical_values.get("QUOTATION_VERSION") == highest]
        if len(highest_records) != 1:
            collector.add("Blocking", "QUOTATION_VERSION_CONFLICT", "Latest quotation version is ambiguous.", sheet="RFQ_QUOTES")
            result.extend(group)
            continue
        for record in group:
            result.append(
                CanonicalRecord(
                    sheet=record.sheet,
                    original_values=record.original_values,
                    canonical_values=record.canonical_values,
                    normalized_values=record.normalized_values,
                    provenance=record.provenance,
                    active=record is highest_records[0],
                )
            )
    return result


def adapt_v13_workbook(
    source: str | Path | bytes | bytearray | BinaryIO,
    *,
    filename: str | None = None,
    selected_sourcing_event_id: str | None = None,
    confirmed_mappings: Iterable[tuple[str, str, str]] = (),
    max_file_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES,
    schema_path: Path = DEFAULT_SCHEMA_PATH,
    alias_path: Path = DEFAULT_ALIAS_PATH,
) -> WorkbookAdapterResult:
    """Safely adapt a v1.3 workbook into governed canonical records.

    The function does not call procurement engines, calculate TCO, score
    suppliers, persist data, mutate the workbook or integrate with SAP.
    """

    resolved_filename = _resolve_filename(source, filename)
    try:
        load_erp_workbook(source, filename=resolved_filename, max_file_size_bytes=max_file_size_bytes)
    except WorkbookLoadError as exc:
        raise WorkbookAdapterError(str(exc)) from exc

    payload = _read_source_bytes(source)
    upload_hash = sha256(payload).hexdigest()
    schema_doc = _load_json(schema_path)
    registry = _load_json(alias_path)
    collector = _FindingCollector()
    confirmed = set(confirmed_mappings)

    workbook = load_workbook(BytesIO(payload), read_only=True, data_only=False, keep_links=False)
    try:
        unknown_sheets = sorted(set(workbook.sheetnames) - set(APPROVED_SHEETS))
        for sheet in unknown_sheets:
            collector.add("Information", "UNKNOWN_SHEET_IGNORED", f"Unknown sheet '{sheet}' is not interpreted.", sheet=sheet)
        if "RFQ_QUOTES" not in workbook.sheetnames:
            collector.add("Fatal", "RFQ_QUOTES_MISSING", "Mandatory sheet 'RFQ_QUOTES' is missing.")

        metadata_records, metadata_reviews = _parse_sheet(
            workbook, "UPLOAD_METADATA", resolved_filename, upload_hash, None,
            schema_doc, registry, collector, confirmed,
        )
        metadata = metadata_records[0].canonical_values if metadata_records else None
        source_hash = None if not metadata else metadata.get("SOURCE_FILE_HASH_SHA256")
        mode = str((metadata or {}).get("UPLOAD_MODE") or ("FULL_SOURCING_REVIEW" if "PO_HISTORY" in workbook.sheetnames else "QUICK_RFQ"))
        if mode not in {"QUICK_RFQ", "FULL_SOURCING_REVIEW"}:
            collector.add("Fatal", "UPLOAD_MODE_INVALID", f"Unsupported upload mode '{mode}'.", sheet="UPLOAD_METADATA", field_name="UPLOAD_MODE")

        rfq_records, rfq_reviews = _parse_sheet(
            workbook, "RFQ_QUOTES", resolved_filename, upload_hash, source_hash,
            schema_doc, registry, collector, confirmed,
        )
        po_records, po_reviews = _parse_sheet(
            workbook, "PO_HISTORY", resolved_filename, upload_hash, source_hash,
            schema_doc, registry, collector, confirmed,
        )
    finally:
        workbook.close()

    if mode == "FULL_SOURCING_REVIEW" and not po_records:
        collector.add("Warning", "PO_HISTORY_UNAVAILABLE", "FULL_SOURCING_REVIEW has no valid PO history rows.", sheet="PO_HISTORY")

    all_records = [*rfq_records, *po_records]
    _validate_positive_fields(all_records, collector)
    _validate_composite_keys(all_records, collector)
    rfq_records = _activate_latest_versions(rfq_records, collector)

    event_ids = tuple(sorted({
        str(record.canonical_values.get("SOURCING_EVENT_ID"))
        for record in rfq_records
        if record.canonical_values.get("SOURCING_EVENT_ID") is not None
    }))
    if len(event_ids) > 1 and selected_sourcing_event_id is None:
        collector.add("Blocking", "SOURCING_EVENT_SELECTION_REQUIRED", "Workbook contains multiple sourcing events; select exactly one before analysis.", sheet="RFQ_QUOTES")
    if selected_sourcing_event_id is not None and selected_sourcing_event_id not in event_ids:
        collector.add("Fatal", "SOURCING_EVENT_SELECTION_INVALID", f"Selected sourcing event '{selected_sourcing_event_id}' is not present.", sheet="RFQ_QUOTES")
    if selected_sourcing_event_id is not None:
        rfq_records = [r for r in rfq_records if str(r.canonical_values.get("SOURCING_EVENT_ID")) == selected_sourcing_event_id]

    active_by_item: dict[tuple[Any, Any], set[Any]] = {}
    for record in rfq_records:
        if not record.active:
            continue
        values = record.canonical_values
        item_key = (values.get("RFQ_NUMBER"), values.get("RFQ_ITEM"))
        active_by_item.setdefault(item_key, set()).add(values.get("SUPPLIER_ID"))
    for item_key, suppliers in active_by_item.items():
        if len({s for s in suppliers if s is not None}) < 2:
            collector.add("Blocking", "MINIMUM_SUPPLIER_COUNT_NOT_MET", f"RFQ item {item_key} has fewer than two valid suppliers.", sheet="RFQ_QUOTES")

    return WorkbookAdapterResult(
        filename=resolved_filename,
        upload_file_hash_sha256=upload_hash,
        mode=mode,
        schema_version=str(schema_doc.get("version", "unknown")),
        alias_registry_version=str(registry.get("registry_version", "unknown")),
        selected_sourcing_event_id=selected_sourcing_event_id,
        available_sourcing_event_ids=event_ids,
        rfq_quotes=tuple(rfq_records),
        po_history=tuple(po_records),
        upload_metadata=dict(metadata) if metadata else None,
        mapping_reviews=tuple([*metadata_reviews, *rfq_reviews, *po_reviews]),
        findings=tuple(collector.findings),
    )
