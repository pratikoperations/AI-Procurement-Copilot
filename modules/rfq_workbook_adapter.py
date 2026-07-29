"""Governed adapter for the v1.3 three-sheet procurement workbook.

The adapter is isolated from procurement calculations, scoring, TCO, UI and
persistence. It preserves source values, produces typed canonical records and
returns validation/mapping evidence only.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import re
from typing import Any, BinaryIO, Iterable, Mapping, Sequence

from openpyxl import load_workbook

from modules.erp_workbook_loader import DEFAULT_MAX_FILE_SIZE_BYTES, WorkbookLoadError, load_erp_workbook

CONTRACT_ROOT = Path(__file__).resolve().parents[1] / "planning" / "v1.3" / "build_group_b"
SCHEMA_PATH = CONTRACT_ROOT / "minimum_workbook_schema_v1.3.0.json"
ALIAS_PATH = CONTRACT_ROOT / "sap_report_alias_registry_v1.3.0.json"
APPROVED_SHEETS = ("RFQ_QUOTES", "PO_HISTORY", "UPLOAD_METADATA")
ROW_DEFS = {"RFQ_QUOTES": "RFQQuoteRow", "PO_HISTORY": "POHistoryRow", "UPLOAD_METADATA": "UploadMetadataRow"}
HIGH_RISK = {
    "SOURCING_EVENT_ID", "RFQ_NUMBER", "RFQ_ITEM", "SUPPLIER_ID", "QUOTATION_VERSION",
    "REQUESTED_QUANTITY", "QUOTED_QUANTITY", "ORDER_QUANTITY", "BASE_UNIT_PRICE",
    "NET_PRICE", "PRICE_UNIT", "CURRENCY", "QUOTATION_UOM", "ORDER_UOM",
    "COMPARISON_UOM", "UOM_CONVERSION_FACTOR", "EXCHANGE_RATE", "EXCHANGE_RATE_DATE",
}
FORMULA_BLOCKING = HIGH_RISK | {
    "QUOTATION_DATE", "VALIDITY_END_DATE", "QUOTATION_STATUS", "PO_DATE", "PO_STATUS",
    "PO_NUMBER", "PO_ITEM", "SOURCE_ROW_ID",
}


@dataclass(frozen=True)
class Finding:
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
class Provenance:
    source_filename: str
    sheet: str
    source_row_number: int
    source_row_id: str
    source_file_hash_sha256: str | None
    upload_file_hash_sha256: str
    schema_version: str
    alias_registry_version: str


@dataclass(frozen=True)
class CanonicalRecord:
    sheet: str
    original_values: Mapping[str, Any]
    canonical_values: Mapping[str, Any]
    normalized_values: Mapping[str, Any]
    provenance: Provenance
    active: bool = True


@dataclass(frozen=True)
class AdapterResult:
    filename: str
    mode: str
    schema_version: str
    alias_registry_version: str
    upload_file_hash_sha256: str
    source_file_hash_sha256: str | None
    selected_sourcing_event_id: str | None
    available_sourcing_event_ids: tuple[str, ...]
    rfq_quotes: tuple[CanonicalRecord, ...]
    po_history: tuple[CanonicalRecord, ...]
    upload_metadata: Mapping[str, Any] | None
    mapping_reviews: tuple[MappingReview, ...]
    findings: tuple[Finding, ...]

    @property
    def has_fatal(self) -> bool:
        return any(item.severity == "Fatal" for item in self.findings)

    @property
    def has_blocking(self) -> bool:
        return any(item.severity == "Blocking" for item in self.findings)


class WorkbookAdapterError(ValueError):
    pass


def _read_bytes(source: str | Path | bytes | bytearray | BinaryIO) -> bytes:
    if isinstance(source, (str, Path)):
        return Path(source).read_bytes()
    if isinstance(source, (bytes, bytearray)):
        return bytes(source)
    read = getattr(source, "read", None)
    if not callable(read):
        raise WorkbookAdapterError("Workbook source must be a path, bytes, or binary file object.")
    position = source.tell() if callable(getattr(source, "tell", None)) else None
    try:
        if callable(getattr(source, "seek", None)):
            source.seek(0)
        payload = read()
    finally:
        if position is not None and callable(getattr(source, "seek", None)):
            source.seek(position)
    if not isinstance(payload, (bytes, bytearray)):
        raise WorkbookAdapterError("Workbook file object must return bytes.")
    return bytes(payload)


def _filename(source: object, supplied: str | None) -> str:
    if supplied:
        return Path(supplied).name
    if isinstance(source, (str, Path)):
        return Path(source).name
    return Path(str(getattr(source, "name", "PROCUREMENT_COPILOT_UPLOAD.xlsx"))).name


def _load_contract(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WorkbookAdapterError(f"Contract file could not be loaded: {path}") from exc


def _normalise_header(value: Any) -> str:
    return re.sub(r"[\W_\s]+", " ", "" if value is None else str(value).strip()).casefold().strip()


def _canonical_alias_index(sheet: str, schema: Mapping[str, Any], registry: Mapping[str, Any]) -> dict[str, list[str]]:
    properties = schema["$defs"][ROW_DEFS[sheet]].get("properties", {})
    aliases = registry.get("sheets", {}).get(sheet, {})
    index: dict[str, list[str]] = {}
    for canonical in properties:
        for label in (canonical, *aliases.get(canonical, [])):
            index.setdefault(_normalise_header(label), []).append(canonical)
    return index


def _map_headers(
    sheet: str,
    headers: Sequence[Any],
    schema: Mapping[str, Any],
    registry: Mapping[str, Any],
    confirmed: set[tuple[str, str, str]],
    findings: list[Finding],
) -> tuple[dict[int, str], list[MappingReview]]:
    index = _canonical_alias_index(sheet, schema, registry)
    aliases = registry.get("sheets", {}).get(sheet, {})
    classes = registry.get("field_source_classifications", {}).get(sheet, {})
    mapped: dict[int, str] = {}
    reviews: list[MappingReview] = []
    used_targets: set[str] = set()
    for position, raw in enumerate(headers):
        source = "" if raw is None else str(raw).strip()
        candidates = tuple(dict.fromkeys(index.get(_normalise_header(raw), [])))
        if not source:
            reviews.append(MappingReview(sheet, source, None, "UNMAPPED", None, False, "Blank header"))
            continue
        if len(candidates) > 1:
            reviews.append(MappingReview(sheet, source, None, "AMBIGUOUS", None, True, f"Matches {candidates}"))
            findings.append(Finding("Fatal", "AMBIGUOUS_HEADER_MAPPING", f"Header '{source}' maps to multiple fields.", sheet))
            continue
        if not candidates:
            reviews.append(MappingReview(sheet, source, None, "UNMAPPED", None, False, "No approved alias"))
            findings.append(Finding("Information", "UNMAPPED_SOURCE_COLUMN", f"Column '{source}' is ignored by calculations.", sheet))
            continue
        canonical = candidates[0]
        if canonical in used_targets:
            reviews.append(MappingReview(sheet, source, canonical, "AMBIGUOUS", classes.get(canonical), True, "Duplicate canonical target"))
            findings.append(Finding("Fatal", "DUPLICATE_CANONICAL_TARGET", f"Multiple columns map to '{canonical}'.", sheet, field_name=canonical))
            continue
        approved_labels = {str(item).strip().casefold() for item in (canonical, *aliases.get(canonical, []))}
        confidence = "EXACT_APPROVED" if source.casefold() in approved_labels else "NORMALIZED_APPROVED"
        needs_confirmation = canonical in HIGH_RISK and confidence != "EXACT_APPROVED"
        if (sheet, source, canonical) in confirmed:
            needs_confirmation = False
        reviews.append(MappingReview(sheet, source, canonical, confidence, classes.get(canonical), needs_confirmation,
                                     "High-risk normalized mapping" if needs_confirmation else None))
        if needs_confirmation:
            findings.append(Finding("Blocking", "HIGH_RISK_MAPPING_CONFIRMATION_REQUIRED",
                                    f"Mapping '{source}' to '{canonical}' requires confirmation.", sheet, field_name=canonical))
        mapped[position] = canonical
        used_targets.add(canonical)
    return mapped, reviews


def _schema_type(property_schema: Mapping[str, Any]) -> str | None:
    reference = property_schema.get("$ref")
    return reference.rsplit("/", 1)[-1] if reference else property_schema.get("type")


def _coerce(value: Any, property_schema: Mapping[str, Any]) -> Any:
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    kind = _schema_type(property_schema)
    if kind == "string":
        return str(value).strip()
    if kind == "integer":
        number = Decimal(str(value))
        if isinstance(value, bool) or number != number.to_integral_value():
            raise ValueError("must be an integer")
        return int(number)
    if kind == "number":
        if isinstance(value, bool):
            raise ValueError("must be numeric")
        return Decimal(str(value))
    if kind == "boolean":
        if isinstance(value, bool):
            return value
        text = str(value).strip().casefold()
        if text in {"true", "yes", "y", "1", "x"}:
            return True
        if text in {"false", "no", "n", "0"}:
            return False
        raise ValueError("must be a recognised boolean")
    if kind == "date":
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        return date.fromisoformat(str(value).strip())
    if kind == "datetime":
        if isinstance(value, datetime):
            return value
        if isinstance(value, date):
            return datetime.combine(value, datetime.min.time())
        return datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    return value


def _empty(values: Iterable[Any]) -> bool:
    return all(value is None or (isinstance(value, str) and not value.strip()) for value in values)


def _parse_sheet(
    workbook: Any,
    sheet: str,
    filename: str,
    upload_hash: str,
    source_hash: str | None,
    schema: Mapping[str, Any],
    registry: Mapping[str, Any],
    confirmed: set[tuple[str, str, str]],
    findings: list[Finding],
) -> tuple[list[CanonicalRecord], list[MappingReview]]:
    if sheet not in workbook.sheetnames:
        return [], []
    worksheet = workbook[sheet]
    rows = worksheet.iter_rows()
    header_cells = next(rows, None)
    if not header_cells:
        findings.append(Finding("Fatal", "EMPTY_SHEET", f"Sheet '{sheet}' has no header row.", sheet))
        return [], []
    headers = [cell.value for cell in header_cells]
    mapped, reviews = _map_headers(sheet, headers, schema, registry, confirmed, findings)
    row_schema = schema["$defs"][ROW_DEFS[sheet]]
    required = set(row_schema.get("required", []))
    for missing in sorted(required - set(mapped.values())):
        findings.append(Finding("Fatal", "MANDATORY_HEADER_MISSING", f"Mandatory field '{missing}' is not mapped.", sheet, field_name=missing))

    records: list[CanonicalRecord] = []
    for row_number, cells in enumerate(rows, start=2):
        values = [cell.value for cell in cells]
        if _empty(values):
            continue
        formulas = {mapped[index] for index, cell in enumerate(cells) if index in mapped and cell.data_type == "f"}
        for field_name in formulas:
            findings.append(Finding("Blocking" if field_name in FORMULA_BLOCKING else "Warning",
                                    "FORMULA_CELL_REJECTED", f"Formula is not accepted for '{field_name}'.",
                                    sheet, row_number, field_name))
        original: dict[str, Any] = {}
        canonical: dict[str, Any] = {}
        for index, value in enumerate(values):
            source_header = str(headers[index]) if index < len(headers) else f"COLUMN_{index + 1}"
            original[source_header] = value
            canonical_name = mapped.get(index)
            if canonical_name is None or canonical_name in formulas:
                continue
            try:
                canonical[canonical_name] = _coerce(value, row_schema.get("properties", {}).get(canonical_name, {}))
            except (ValueError, TypeError, InvalidOperation) as exc:
                severity = "Fatal" if canonical_name in required else "Blocking"
                findings.append(Finding(severity, "VALUE_TYPE_INVALID", f"Invalid '{canonical_name}': {exc}",
                                        sheet, row_number, canonical_name))
                canonical[canonical_name] = None
        for required_field in required:
            if canonical.get(required_field) is None:
                findings.append(Finding("Fatal", "MANDATORY_VALUE_MISSING", f"Mandatory value '{required_field}' is missing.",
                                        sheet, row_number, required_field))
        row_id = str(canonical.get("SOURCE_ROW_ID") or f"{sheet}:{row_number}")
        records.append(CanonicalRecord(
            sheet=sheet,
            original_values=original,
            canonical_values=canonical,
            normalized_values={},
            provenance=Provenance(filename, sheet, row_number, row_id, source_hash, upload_hash,
                                  str(schema.get("version", "unknown")), str(registry.get("registry_version", "unknown"))),
        ))
    return records, reviews


def _validate_values(records: Sequence[CanonicalRecord], findings: list[Finding]) -> None:
    positive = {"REQUESTED_QUANTITY", "QUOTED_QUANTITY", "ORDER_QUANTITY", "PRICE_UNIT", "UOM_CONVERSION_FACTOR", "EXCHANGE_RATE"}
    non_negative = {"BASE_UNIT_PRICE", "NET_PRICE", "NET_ORDER_VALUE"}
    for record in records:
        for field_name in positive:
            value = record.canonical_values.get(field_name)
            if value is not None and value <= 0:
                findings.append(Finding("Blocking", "POSITIVE_VALUE_REQUIRED", f"'{field_name}' must be greater than zero.",
                                        record.sheet, record.provenance.source_row_number, field_name))
        for field_name in non_negative:
            value = record.canonical_values.get(field_name)
            if value is not None and value < 0:
                findings.append(Finding("Blocking", "NEGATIVE_VALUE_REJECTED", f"'{field_name}' cannot be negative.",
                                        record.sheet, record.provenance.source_row_number, field_name))


def _validate_keys(records: Sequence[CanonicalRecord], findings: list[Finding]) -> None:
    key_fields = {
        "RFQ_QUOTES": ("SOURCING_EVENT_ID", "RFQ_NUMBER", "RFQ_ITEM", "SUPPLIER_ID", "QUOTATION_VERSION"),
        "PO_HISTORY": ("PO_NUMBER", "PO_ITEM"),
    }
    seen: dict[tuple[str, tuple[Any, ...]], Mapping[str, Any]] = {}
    for record in records:
        fields = key_fields.get(record.sheet)
        if not fields:
            continue
        key = tuple(record.canonical_values.get(name) for name in fields)
        compound = (record.sheet, key)
        prior = seen.get(compound)
        if prior is None:
            seen[compound] = record.canonical_values
        elif dict(prior) != dict(record.canonical_values):
            findings.append(Finding("Fatal", "CONTRADICTORY_DUPLICATE_KEY", f"Contradictory duplicate key {key}.", record.sheet,
                                    record.provenance.source_row_number))
        else:
            findings.append(Finding("Warning", "EXACT_DUPLICATE_ROW", f"Exact duplicate key {key}.", record.sheet,
                                    record.provenance.source_row_number))


def _select_latest_versions(records: Sequence[CanonicalRecord], findings: list[Finding]) -> list[CanonicalRecord]:
    groups: dict[tuple[Any, ...], list[CanonicalRecord]] = {}
    for record in records:
        values = record.canonical_values
        key = (values.get("SOURCING_EVENT_ID"), values.get("RFQ_NUMBER"), values.get("RFQ_ITEM"), values.get("SUPPLIER_ID"))
        groups.setdefault(key, []).append(record)
    result: list[CanonicalRecord] = []
    for group in groups.values():
        versions = [item.canonical_values.get("QUOTATION_VERSION") for item in group]
        valid = [value for value in versions if isinstance(value, int)]
        if not valid:
            result.extend(group)
            continue
        latest = max(valid)
        latest_records = [item for item in group if item.canonical_values.get("QUOTATION_VERSION") == latest]
        if len(latest_records) != 1:
            findings.append(Finding("Blocking", "QUOTATION_VERSION_CONFLICT", "Latest quotation version is ambiguous.", "RFQ_QUOTES"))
            result.extend(group)
            continue
        winner = latest_records[0]
        result.extend(CanonicalRecord(item.sheet, item.original_values, item.canonical_values,
                                      item.normalized_values, item.provenance, item is winner) for item in group)
    return result


def adapt_v13_workbook(
    source: str | Path | bytes | bytearray | BinaryIO,
    *,
    filename: str | None = None,
    selected_sourcing_event_id: str | None = None,
    confirmed_mappings: Iterable[tuple[str, str, str]] = (),
    max_file_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES,
    schema_path: Path = SCHEMA_PATH,
    alias_path: Path = ALIAS_PATH,
) -> AdapterResult:
    """Return typed adapter evidence without invoking downstream engines."""
    resolved_filename = _filename(source, filename)
    try:
        load_erp_workbook(source, filename=resolved_filename, max_file_size_bytes=max_file_size_bytes)
    except WorkbookLoadError as exc:
        raise WorkbookAdapterError(str(exc)) from exc
    payload = _read_bytes(source)
    upload_hash = sha256(payload).hexdigest()
    schema = _load_contract(schema_path)
    registry = _load_contract(alias_path)
    findings: list[Finding] = []
    confirmed = set(confirmed_mappings)

    workbook = load_workbook(BytesIO(payload), read_only=True, data_only=False, keep_links=False)
    try:
        for unknown in sorted(set(workbook.sheetnames) - set(APPROVED_SHEETS)):
            findings.append(Finding("Information", "UNKNOWN_SHEET_IGNORED", f"Unknown sheet '{unknown}' is not interpreted.", unknown))
        if "RFQ_QUOTES" not in workbook.sheetnames:
            findings.append(Finding("Fatal", "RFQ_QUOTES_MISSING", "Mandatory sheet 'RFQ_QUOTES' is missing."))
        metadata_records, metadata_reviews = _parse_sheet(workbook, "UPLOAD_METADATA", resolved_filename, upload_hash, None,
                                                           schema, registry, confirmed, findings)
        metadata = dict(metadata_records[0].canonical_values) if metadata_records else None
        source_hash = None if metadata is None else metadata.get("SOURCE_FILE_HASH_SHA256")
        mode = str((metadata or {}).get("UPLOAD_MODE") or ("FULL_SOURCING_REVIEW" if "PO_HISTORY" in workbook.sheetnames else "QUICK_RFQ"))
        if mode not in {"QUICK_RFQ", "FULL_SOURCING_REVIEW"}:
            findings.append(Finding("Fatal", "UPLOAD_MODE_INVALID", f"Unsupported upload mode '{mode}'.", "UPLOAD_METADATA", field_name="UPLOAD_MODE"))
        rfq_records, rfq_reviews = _parse_sheet(workbook, "RFQ_QUOTES", resolved_filename, upload_hash, source_hash,
                                                 schema, registry, confirmed, findings)
        po_records, po_reviews = _parse_sheet(workbook, "PO_HISTORY", resolved_filename, upload_hash, source_hash,
                                               schema, registry, confirmed, findings)
    finally:
        workbook.close()

    if mode == "FULL_SOURCING_REVIEW" and not po_records:
        findings.append(Finding("Warning", "PO_HISTORY_UNAVAILABLE", "Full review has no valid PO history rows.", "PO_HISTORY"))
    _validate_values([*rfq_records, *po_records], findings)
    _validate_keys([*rfq_records, *po_records], findings)
    rfq_records = _select_latest_versions(rfq_records, findings)

    event_ids = tuple(sorted({str(item.canonical_values["SOURCING_EVENT_ID"]) for item in rfq_records
                              if item.canonical_values.get("SOURCING_EVENT_ID") is not None}))
    if len(event_ids) > 1 and selected_sourcing_event_id is None:
        findings.append(Finding("Blocking", "SOURCING_EVENT_SELECTION_REQUIRED",
                                "Multiple sourcing events require explicit selection.", "RFQ_QUOTES"))
    if selected_sourcing_event_id is not None and selected_sourcing_event_id not in event_ids:
        findings.append(Finding("Fatal", "SOURCING_EVENT_SELECTION_INVALID",
                                f"Selected sourcing event '{selected_sourcing_event_id}' is not present.", "RFQ_QUOTES"))
    if selected_sourcing_event_id is not None:
        rfq_records = [item for item in rfq_records
                       if str(item.canonical_values.get("SOURCING_EVENT_ID")) == selected_sourcing_event_id]

    suppliers_by_item: dict[tuple[Any, Any], set[Any]] = {}
    for item in rfq_records:
        if item.active:
            values = item.canonical_values
            suppliers_by_item.setdefault((values.get("RFQ_NUMBER"), values.get("RFQ_ITEM")), set()).add(values.get("SUPPLIER_ID"))
    for item_key, suppliers in suppliers_by_item.items():
        if len({supplier for supplier in suppliers if supplier is not None}) < 2:
            findings.append(Finding("Blocking", "MINIMUM_SUPPLIER_COUNT_NOT_MET",
                                    f"RFQ item {item_key} has fewer than two valid suppliers.", "RFQ_QUOTES"))

    return AdapterResult(
        filename=resolved_filename,
        mode=mode,
        schema_version=str(schema.get("version", "unknown")),
        alias_registry_version=str(registry.get("registry_version", "unknown")),
        upload_file_hash_sha256=upload_hash,
        source_file_hash_sha256=source_hash,
        selected_sourcing_event_id=selected_sourcing_event_id,
        available_sourcing_event_ids=event_ids,
        rfq_quotes=tuple(rfq_records),
        po_history=tuple(po_records),
        upload_metadata=metadata,
        mapping_reviews=tuple([*metadata_reviews, *rfq_reviews, *po_reviews]),
        findings=tuple(findings),
    )
