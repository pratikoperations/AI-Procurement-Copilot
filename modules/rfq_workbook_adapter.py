"""Governed adapter for the v1.3 three-sheet procurement workbook.

The adapter is isolated from procurement calculations, scoring, TCO, UI and
persistence. It preserves source values, produces typed canonical records and
returns validation/mapping evidence only.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
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
SCHEMA_PATH = CONTRACT_ROOT / "minimum_workbook_schema_v1.3.0.json"
ALIAS_PATH = CONTRACT_ROOT / "sap_report_alias_registry_v1.3.0.json"
APPROVED_SHEETS = ("RFQ_QUOTES", "PO_HISTORY", "UPLOAD_METADATA")
ROW_DEFS = {
    "RFQ_QUOTES": "RFQQuoteRow",
    "PO_HISTORY": "POHistoryRow",
    "UPLOAD_METADATA": "UploadMetadataRow",
}
HIGH_RISK = {
    "SOURCING_EVENT_ID",
    "RFQ_NUMBER",
    "RFQ_ITEM",
    "SUPPLIER_ID",
    "QUOTATION_VERSION",
    "REQUESTED_QUANTITY",
    "QUOTED_QUANTITY",
    "ORDER_QUANTITY",
    "BASE_UNIT_PRICE",
    "NET_PRICE",
    "PRICE_UNIT",
    "CURRENCY",
    "QUOTATION_UOM",
    "ORDER_UOM",
    "COMPARISON_UOM",
    "UOM_CONVERSION_FACTOR",
    "EXCHANGE_RATE",
    "EXCHANGE_RATE_DATE",
}
FORMULA_BLOCKING = HIGH_RISK | {
    "QUOTATION_DATE",
    "VALIDITY_END_DATE",
    "QUOTATION_STATUS",
    "PO_DATE",
    "PO_STATUS",
    "PO_NUMBER",
    "PO_ITEM",
    "SOURCE_ROW_ID",
}
PROVENANCE_ONLY_FIELDS = {
    "SOURCE_ROW_ID",
    "SOURCE_FILE_NAME",
    "SOURCE_EXTRACTED_AT",
}
SHEET_LEVEL_ROW_BLOCKING_CODES = {
    "AMBIGUOUS_HEADER_MAPPING",
    "DUPLICATE_CANONICAL_TARGET",
    "HIGH_RISK_MAPPING_CONFIRMATION_REQUIRED",
    "MANDATORY_HEADER_MISSING",
}
VALIDITY_SEVERITIES = {"Fatal", "Blocking"}


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
    valid_for_analysis: bool = True


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
    """Raised when the workbook cannot enter the governed adapter."""


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


def _canonical_alias_index(
    sheet: str,
    schema: Mapping[str, Any],
    registry: Mapping[str, Any],
) -> dict[str, list[str]]:
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
            reviews.append(
                MappingReview(
                    sheet,
                    source,
                    None,
                    "AMBIGUOUS",
                    None,
                    True,
                    f"Matches {candidates}",
                )
            )
            findings.append(
                Finding(
                    "Fatal",
                    "AMBIGUOUS_HEADER_MAPPING",
                    f"Header '{source}' maps to multiple fields.",
                    sheet,
                )
            )
            continue
        if not candidates:
            reviews.append(
                MappingReview(sheet, source, None, "UNMAPPED", None, False, "No approved alias")
            )
            findings.append(
                Finding(
                    "Information",
                    "UNMAPPED_SOURCE_COLUMN",
                    f"Column '{source}' is ignored by calculations.",
                    sheet,
                )
            )
            continue

        canonical = candidates[0]
        if canonical in used_targets:
            reviews.append(
                MappingReview(
                    sheet,
                    source,
                    canonical,
                    "AMBIGUOUS",
                    classes.get(canonical),
                    True,
                    "Duplicate canonical target",
                )
            )
            findings.append(
                Finding(
                    "Fatal",
                    "DUPLICATE_CANONICAL_TARGET",
                    f"Multiple columns map to '{canonical}'.",
                    sheet,
                    field_name=canonical,
                )
            )
            continue

        approved_labels = {
            str(item).strip().casefold()
            for item in (canonical, *aliases.get(canonical, []))
        }
        confidence = (
            "EXACT_APPROVED" if source.casefold() in approved_labels else "NORMALIZED_APPROVED"
        )
        needs_confirmation = canonical in HIGH_RISK and confidence != "EXACT_APPROVED"
        if (sheet, source, canonical) in confirmed:
            needs_confirmation = False
        reviews.append(
            MappingReview(
                sheet,
                source,
                canonical,
                confidence,
                classes.get(canonical),
                needs_confirmation,
                "High-risk normalized mapping" if needs_confirmation else None,
            )
        )
        if needs_confirmation:
            findings.append(
                Finding(
                    "Blocking",
                    "HIGH_RISK_MAPPING_CONFIRMATION_REQUIRED",
                    f"Mapping '{source}' to '{canonical}' requires confirmation.",
                    sheet,
                    field_name=canonical,
                )
            )
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
        findings.append(
            Finding(
                "Fatal",
                "MANDATORY_HEADER_MISSING",
                f"Mandatory field '{missing}' is not mapped.",
                sheet,
                field_name=missing,
            )
        )

    records: list[CanonicalRecord] = []
    for row_number, cells in enumerate(rows, start=2):
        values = [cell.value for cell in cells]
        if _empty(values):
            continue

        formulas = {
            mapped[index]
            for index, cell in enumerate(cells)
            if index in mapped and cell.data_type == "f"
        }
        for field_name in formulas:
            findings.append(
                Finding(
                    "Blocking" if field_name in FORMULA_BLOCKING else "Warning",
                    "FORMULA_CELL_REJECTED",
                    f"Formula is not accepted for '{field_name}'.",
                    sheet,
                    row_number,
                    field_name,
                )
            )

        original: dict[str, Any] = {}
        canonical: dict[str, Any] = {}
        for index, value in enumerate(values):
            source_header = (
                str(headers[index]) if index < len(headers) else f"COLUMN_{index + 1}"
            )
            original[source_header] = value
            canonical_name = mapped.get(index)
            if canonical_name is None or canonical_name in formulas:
                continue
            try:
                canonical[canonical_name] = _coerce(
                    value,
                    row_schema.get("properties", {}).get(canonical_name, {}),
                )
            except (ValueError, TypeError, InvalidOperation) as exc:
                severity = "Fatal" if canonical_name in required else "Blocking"
                findings.append(
                    Finding(
                        severity,
                        "VALUE_TYPE_INVALID",
                        f"Invalid '{canonical_name}': {exc}",
                        sheet,
                        row_number,
                        canonical_name,
                    )
                )
                canonical[canonical_name] = None

        for required_field in required:
            if canonical.get(required_field) is None:
                findings.append(
                    Finding(
                        "Fatal",
                        "MANDATORY_VALUE_MISSING",
                        f"Mandatory value '{required_field}' is missing.",
                        sheet,
                        row_number,
                        required_field,
                    )
                )

        row_id = str(canonical.get("SOURCE_ROW_ID") or f"{sheet}:{row_number}")
        records.append(
            CanonicalRecord(
                sheet=sheet,
                original_values=original,
                canonical_values=canonical,
                normalized_values={},
                provenance=Provenance(
                    filename,
                    sheet,
                    row_number,
                    row_id,
                    source_hash,
                    upload_hash,
                    str(schema.get("version", "unknown")),
                    str(registry.get("registry_version", "unknown")),
                ),
            )
        )

    return records, reviews


def _validate_values(records: Sequence[CanonicalRecord], findings: list[Finding]) -> None:
    positive = {
        "REQUESTED_QUANTITY",
        "QUOTED_QUANTITY",
        "ORDER_QUANTITY",
        "PRICE_UNIT",
        "UOM_CONVERSION_FACTOR",
        "EXCHANGE_RATE",
    }
    non_negative = {
        "BASE_UNIT_PRICE",
        "NET_PRICE",
        "NET_ORDER_VALUE",
        "FREIGHT_AMOUNT",
        "PACKING_AMOUNT",
        "INSURANCE_AMOUNT",
        "DUTY_AMOUNT",
        "TAX_AMOUNT",
        "TOOLING_AMOUNT",
        "OTHER_CHARGES_AMOUNT",
    }
    for record in records:
        for field_name in positive:
            value = record.canonical_values.get(field_name)
            if value is not None and value <= 0:
                findings.append(
                    Finding(
                        "Blocking",
                        "POSITIVE_VALUE_REQUIRED",
                        f"'{field_name}' must be greater than zero.",
                        record.sheet,
                        record.provenance.source_row_number,
                        field_name,
                    )
                )
        for field_name in non_negative:
            value = record.canonical_values.get(field_name)
            if value is not None and value < 0:
                findings.append(
                    Finding(
                        "Blocking",
                        "NEGATIVE_VALUE_REJECTED",
                        f"'{field_name}' cannot be negative.",
                        record.sheet,
                        record.provenance.source_row_number,
                        field_name,
                    )
                )


def _business_payload(record: CanonicalRecord) -> dict[str, Any]:
    return {
        key: value
        for key, value in record.canonical_values.items()
        if key not in PROVENANCE_ONLY_FIELDS
    }


def _validate_keys(records: Sequence[CanonicalRecord], findings: list[Finding]) -> None:
    key_fields = {
        "RFQ_QUOTES": (
            "SOURCING_EVENT_ID",
            "RFQ_NUMBER",
            "RFQ_ITEM",
            "SUPPLIER_ID",
            "QUOTATION_VERSION",
        ),
        "PO_HISTORY": ("PO_NUMBER", "PO_ITEM"),
    }
    seen: dict[tuple[str, tuple[Any, ...]], CanonicalRecord] = {}
    for record in records:
        fields = key_fields.get(record.sheet)
        if not fields:
            continue
        key = tuple(record.canonical_values.get(name) for name in fields)
        compound = (record.sheet, key)
        prior = seen.get(compound)
        if prior is None:
            seen[compound] = record
        elif _business_payload(prior) != _business_payload(record):
            findings.append(
                Finding(
                    "Fatal",
                    "CONTRADICTORY_DUPLICATE_KEY",
                    f"Contradictory duplicate key {key}.",
                    record.sheet,
                    record.provenance.source_row_number,
                )
            )
        else:
            findings.append(
                Finding(
                    "Warning",
                    "EXACT_DUPLICATE_ROW",
                    f"Duplicate business payload for key {key}.",
                    record.sheet,
                    record.provenance.source_row_number,
                )
            )


def _select_latest_versions(
    records: Sequence[CanonicalRecord],
    findings: list[Finding],
) -> list[CanonicalRecord]:
    groups: dict[tuple[Any, ...], list[CanonicalRecord]] = {}
    for record in records:
        values = record.canonical_values
        key = (
            values.get("SOURCING_EVENT_ID"),
            values.get("RFQ_NUMBER"),
            values.get("RFQ_ITEM"),
            values.get("SUPPLIER_ID"),
        )
        groups.setdefault(key, []).append(record)

    result: list[CanonicalRecord] = []
    for group in groups.values():
        versions = [item.canonical_values.get("QUOTATION_VERSION") for item in group]
        valid = [value for value in versions if isinstance(value, int)]
        if not valid:
            result.extend(group)
            continue
        latest = max(valid)
        latest_records = [
            item
            for item in group
            if item.canonical_values.get("QUOTATION_VERSION") == latest
        ]
        if len(latest_records) != 1:
            findings.append(
                Finding(
                    "Blocking",
                    "QUOTATION_VERSION_CONFLICT",
                    "Latest quotation version is ambiguous.",
                    "RFQ_QUOTES",
                )
            )
            result.extend(group)
            continue
        winner = latest_records[0]
        result.extend(replace(item, active=item is winner) for item in group)
    return result


def _validate_metadata(
    metadata_records: Sequence[CanonicalRecord],
    schema: Mapping[str, Any],
    findings: list[Finding],
) -> Mapping[str, Any] | None:
    if len(metadata_records) > 1:
        findings.append(
            Finding(
                "Fatal",
                "UPLOAD_METADATA_CARDINALITY_INVALID",
                "UPLOAD_METADATA may contain at most one non-empty data row.",
                "UPLOAD_METADATA",
            )
        )
    if not metadata_records:
        return None

    metadata = dict(metadata_records[0].canonical_values)
    constraints = schema.get("x-field-constraints", {})
    expected_version = str(constraints.get("schema_version_const", schema.get("version", "1.3.0")))
    actual_version = metadata.get("SCHEMA_VERSION")
    if str(actual_version or "") != expected_version:
        findings.append(
            Finding(
                "Fatal",
                "SCHEMA_VERSION_UNSUPPORTED",
                f"SCHEMA_VERSION must equal '{expected_version}'.",
                "UPLOAD_METADATA",
                metadata_records[0].provenance.source_row_number,
                "SCHEMA_VERSION",
            )
        )

    upload_modes = set(constraints.get("upload_mode_enum", ()))
    upload_mode = metadata.get("UPLOAD_MODE")
    if upload_mode is not None and upload_modes and upload_mode not in upload_modes:
        findings.append(
            Finding(
                "Fatal",
                "UPLOAD_MODE_INVALID",
                f"Unsupported upload mode '{upload_mode}'.",
                "UPLOAD_METADATA",
                metadata_records[0].provenance.source_row_number,
                "UPLOAD_MODE",
            )
        )

    anonymization_values = set(constraints.get("anonymization_enum", ()))
    anonymization = metadata.get("ANONYMIZATION_STATUS")
    if (
        anonymization is not None
        and anonymization_values
        and anonymization not in anonymization_values
    ):
        findings.append(
            Finding(
                "Blocking",
                "ANONYMIZATION_STATUS_INVALID",
                f"ANONYMIZATION_STATUS must be one of {sorted(anonymization_values)}.",
                "UPLOAD_METADATA",
                metadata_records[0].provenance.source_row_number,
                "ANONYMIZATION_STATUS",
            )
        )

    hash_pattern = constraints.get("sha256_pattern", r"^[a-fA-F0-9]{64}$")
    source_hash = metadata.get("SOURCE_FILE_HASH_SHA256")
    if source_hash is None or re.fullmatch(hash_pattern, str(source_hash)) is None:
        findings.append(
            Finding(
                "Blocking",
                "SOURCE_FILE_HASH_INVALID",
                "SOURCE_FILE_HASH_SHA256 must contain exactly 64 hexadecimal characters.",
                "UPLOAD_METADATA",
                metadata_records[0].provenance.source_row_number,
                "SOURCE_FILE_HASH_SHA256",
            )
        )

    currency_pattern = constraints.get("currency_pattern", r"^[A-Z]{3}$")
    base_currency = metadata.get("BASE_CURRENCY")
    if base_currency is not None and re.fullmatch(currency_pattern, str(base_currency)) is None:
        findings.append(
            Finding(
                "Blocking",
                "CURRENCY_FORMAT_INVALID",
                "BASE_CURRENCY must be a three-letter uppercase currency code.",
                "UPLOAD_METADATA",
                metadata_records[0].provenance.source_row_number,
                "BASE_CURRENCY",
            )
        )

    return metadata


def _validate_row_currencies(
    records: Sequence[CanonicalRecord],
    schema: Mapping[str, Any],
    findings: list[Finding],
) -> None:
    pattern = schema.get("x-field-constraints", {}).get(
        "currency_pattern",
        r"^[A-Z]{3}$",
    )
    for record in records:
        currency = record.canonical_values.get("CURRENCY")
        if currency is not None and re.fullmatch(pattern, str(currency)) is None:
            findings.append(
                Finding(
                    "Blocking",
                    "CURRENCY_FORMAT_INVALID",
                    "CURRENCY must be a three-letter uppercase currency code.",
                    record.sheet,
                    record.provenance.source_row_number,
                    "CURRENCY",
                )
            )


def _record_is_valid(record: CanonicalRecord, findings: Sequence[Finding]) -> bool:
    row_number = record.provenance.source_row_number
    for finding in findings:
        if finding.severity not in VALIDITY_SEVERITIES or finding.sheet != record.sheet:
            continue
        if finding.row_number == row_number:
            return False
        if (
            finding.row_number is None
            and finding.code in SHEET_LEVEL_ROW_BLOCKING_CODES
        ):
            return False
    return True


def _apply_record_validity(
    records: Sequence[CanonicalRecord],
    findings: Sequence[Finding],
) -> list[CanonicalRecord]:
    return [
        replace(record, valid_for_analysis=_record_is_valid(record, findings))
        for record in records
    ]


def _validate_no_valid_rfq(
    rfq_records: Sequence[CanonicalRecord],
    findings: list[Finding],
    *,
    selected_event: str | None,
) -> None:
    if not rfq_records:
        findings.append(
            Finding(
                "Fatal",
                "RFQ_QUOTES_EMPTY",
                "RFQ_QUOTES must contain at least one non-empty quotation row.",
                "RFQ_QUOTES",
            )
        )
        return

    valid_active = [
        item for item in rfq_records if item.active and item.valid_for_analysis
    ]
    if not valid_active:
        code = (
            "NO_VALID_SELECTED_EVENT_QUOTATIONS"
            if selected_event is not None
            else "NO_VALID_QUOTATION_RECORDS"
        )
        message = (
            f"No valid active quotation records remain for selected event '{selected_event}'."
            if selected_event is not None
            else "No valid active quotation records remain after adapter validation."
        )
        findings.append(Finding("Fatal", code, message, "RFQ_QUOTES"))


def _validate_supplier_counts(
    rfq_records: Sequence[CanonicalRecord],
    findings: list[Finding],
) -> None:
    suppliers_by_item: dict[tuple[Any, Any], set[Any]] = {}
    for item in rfq_records:
        if not item.active or not item.valid_for_analysis:
            continue
        values = item.canonical_values
        suppliers_by_item.setdefault(
            (values.get("RFQ_NUMBER"), values.get("RFQ_ITEM")),
            set(),
        ).add(values.get("SUPPLIER_ID"))

    for item_key, suppliers in suppliers_by_item.items():
        valid_suppliers = {supplier for supplier in suppliers if supplier is not None}
        if len(valid_suppliers) < 2:
            findings.append(
                Finding(
                    "Blocking",
                    "MINIMUM_SUPPLIER_COUNT_NOT_MET",
                    f"RFQ item {item_key} has fewer than two valid suppliers.",
                    "RFQ_QUOTES",
                )
            )


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
        load_erp_workbook(
            source,
            filename=resolved_filename,
            max_file_size_bytes=max_file_size_bytes,
        )
    except WorkbookLoadError as exc:
        raise WorkbookAdapterError(str(exc)) from exc

    payload = _read_bytes(source)
    upload_hash = sha256(payload).hexdigest()
    schema = _load_contract(schema_path)
    registry = _load_contract(alias_path)
    findings: list[Finding] = []
    confirmed = set(confirmed_mappings)

    workbook = load_workbook(
        BytesIO(payload),
        read_only=True,
        data_only=False,
        keep_links=False,
    )
    try:
        for unknown in sorted(set(workbook.sheetnames) - set(APPROVED_SHEETS)):
            findings.append(
                Finding(
                    "Information",
                    "UNKNOWN_SHEET_IGNORED",
                    f"Unknown sheet '{unknown}' is not interpreted.",
                    unknown,
                )
            )
        if "RFQ_QUOTES" not in workbook.sheetnames:
            findings.append(
                Finding(
                    "Fatal",
                    "RFQ_QUOTES_MISSING",
                    "Mandatory sheet 'RFQ_QUOTES' is missing.",
                )
            )

        metadata_records, metadata_reviews = _parse_sheet(
            workbook,
            "UPLOAD_METADATA",
            resolved_filename,
            upload_hash,
            None,
            schema,
            registry,
            confirmed,
            findings,
        )
        metadata = _validate_metadata(metadata_records, schema, findings)
        source_hash = None if metadata is None else metadata.get("SOURCE_FILE_HASH_SHA256")
        inferred_mode = (
            "FULL_SOURCING_REVIEW"
            if "PO_HISTORY" in workbook.sheetnames
            else "QUICK_RFQ"
        )
        mode = str((metadata or {}).get("UPLOAD_MODE") or inferred_mode)

        rfq_records, rfq_reviews = _parse_sheet(
            workbook,
            "RFQ_QUOTES",
            resolved_filename,
            upload_hash,
            source_hash,
            schema,
            registry,
            confirmed,
            findings,
        )
        po_records, po_reviews = _parse_sheet(
            workbook,
            "PO_HISTORY",
            resolved_filename,
            upload_hash,
            source_hash,
            schema,
            registry,
            confirmed,
            findings,
        )
    finally:
        workbook.close()

    if mode == "FULL_SOURCING_REVIEW" and not po_records:
        findings.append(
            Finding(
                "Warning",
                "PO_HISTORY_UNAVAILABLE",
                "Full review has no valid PO history rows.",
                "PO_HISTORY",
            )
        )

    _validate_values([*rfq_records, *po_records], findings)
    _validate_row_currencies([*rfq_records, *po_records], schema, findings)
    _validate_keys([*rfq_records, *po_records], findings)
    rfq_records = _select_latest_versions(rfq_records, findings)

    event_ids = tuple(
        sorted(
            {
                str(item.canonical_values["SOURCING_EVENT_ID"])
                for item in rfq_records
                if item.canonical_values.get("SOURCING_EVENT_ID") is not None
            }
        )
    )
    if len(event_ids) > 1 and selected_sourcing_event_id is None:
        findings.append(
            Finding(
                "Blocking",
                "SOURCING_EVENT_SELECTION_REQUIRED",
                "Multiple sourcing events require explicit selection.",
                "RFQ_QUOTES",
            )
        )
    if (
        selected_sourcing_event_id is not None
        and selected_sourcing_event_id not in event_ids
    ):
        findings.append(
            Finding(
                "Fatal",
                "SOURCING_EVENT_SELECTION_INVALID",
                f"Selected sourcing event '{selected_sourcing_event_id}' is not present.",
                "RFQ_QUOTES",
            )
        )
    if selected_sourcing_event_id is not None:
        rfq_records = [
            item
            for item in rfq_records
            if str(item.canonical_values.get("SOURCING_EVENT_ID"))
            == selected_sourcing_event_id
        ]

    rfq_records = _apply_record_validity(rfq_records, findings)
    po_records = _apply_record_validity(po_records, findings)
    _validate_no_valid_rfq(
        rfq_records,
        findings,
        selected_event=selected_sourcing_event_id,
    )
    _validate_supplier_counts(rfq_records, findings)

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
