from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path

from openpyxl import Workbook
import pytest

from modules.rfq_workbook_adapter import (
    ALIAS_PATH,
    SCHEMA_PATH,
    WorkbookAdapterError,
    adapt_v13_workbook,
)


def _schema() -> dict:
    return json.loads(Path(SCHEMA_PATH).read_text(encoding="utf-8"))


def _required_headers(definition: str) -> list[str]:
    return list(_schema()["$defs"][definition]["required"])


def _value(field: str, supplier: str = "0000100001", event: str = "EVT-001", version: int = 1):
    values = {
        "SOURCING_EVENT_ID": event,
        "RFQ_NUMBER": "0010000001",
        "RFQ_ITEM": "00010",
        "QUOTATION_VERSION": version,
        "SUPPLIER_ID": supplier,
        "SUPPLIER_NAME": f"Supplier {supplier[-1]}",
        "MATERIAL_DESCRIPTION": "Synthetic carton",
        "MATERIAL_GROUP": "PACK",
        "PURCHASING_ORG": "1000",
        "REQUESTED_QUANTITY": 1000,
        "QUOTED_QUANTITY": 1000,
        "QUOTATION_UOM": "EA",
        "COMPARISON_UOM": "EA",
        "BASE_UNIT_PRICE": 12.5,
        "PRICE_UNIT": 1,
        "CURRENCY": "INR",
        "QUOTATION_DATE": "2026-07-01",
        "VALIDITY_END_DATE": "2026-12-31",
        "QUOTATION_STATUS": "VALID",
        "SOURCE_TRANSACTION": "ME49",
        "SOURCE_FILE_NAME": "synthetic_rfq.xlsx",
        "SOURCE_EXTRACTED_AT": "2026-07-29T10:00:00",
        "SOURCE_ROW_ID": f"RFQ-{supplier}-{version}",
        "PO_NUMBER": "0045000001",
        "PO_ITEM": "00010",
        "PO_DATE": "2026-06-01",
        "ORDER_QUANTITY": 1000,
        "ORDER_UOM": "EA",
        "NET_PRICE": 12.0,
        "NET_ORDER_VALUE": 12000,
        "PO_STATUS": "COMPLETE",
        "DELETION_FLAG": False,
    }
    return values.get(field, "SYNTHETIC")


def _append_row(ws, headers: list[str], *, supplier: str, event: str = "EVT-001", version: int = 1):
    ws.append([_value(header, supplier, event, version) for header in headers])


def _workbook_bytes(
    *,
    include_history: bool = True,
    include_metadata: bool = True,
    second_event: bool = False,
    formula_price: bool = False,
    alias_header: bool = False,
) -> bytes:
    wb = Workbook()
    rfq = wb.active
    rfq.title = "RFQ_QUOTES"
    headers = _required_headers("RFQQuoteRow")
    if alias_header:
        headers[headers.index("RFQ_NUMBER")] = "RFQ-Number"
    rfq.append(headers)
    _append_row(rfq, headers, supplier="0000100001")
    _append_row(rfq, headers, supplier="0000100002")
    if second_event:
        _append_row(rfq, headers, supplier="0000100003", event="EVT-002")
        _append_row(rfq, headers, supplier="0000100004", event="EVT-002")
    if formula_price:
        price_column = headers.index("BASE_UNIT_PRICE") + 1
        rfq.cell(row=2, column=price_column, value="=10+2.5")

    if include_history:
        history = wb.create_sheet("PO_HISTORY")
        history_headers = _required_headers("POHistoryRow")
        history.append(history_headers)
        _append_row(history, history_headers, supplier="0000100001")

    if include_metadata:
        metadata = wb.create_sheet("UPLOAD_METADATA")
        metadata_headers = [
            "UPLOAD_ID", "SCHEMA_VERSION", "UPLOAD_MODE", "SOURCE_SYSTEM",
            "PURCHASING_ORG", "BASE_CURRENCY", "EXTRACTED_AT", "UPLOAD_CREATED_AT",
            "RFQ_SOURCE_TRANSACTION", "DATA_CLASSIFICATION", "ANONYMIZATION_STATUS",
            "SOURCE_FILE_HASH_SHA256", "NOTES",
        ]
        metadata.append(metadata_headers)
        metadata.append([
            "UP-001", "1.3.0", "FULL_SOURCING_REVIEW" if include_history else "QUICK_RFQ",
            "SAP", "1000", "INR", "2026-07-29T10:00:00", "2026-07-29T10:05:00",
            "ME49", "SYNTHETIC", "SYNTHETIC", "a" * 64,
            "Canonical upload hash is calculated externally during ingestion.",
        ])

    stream = BytesIO()
    wb.save(stream)
    wb.close()
    return stream.getvalue()


def test_full_workbook_parses_typed_records_and_hashes():
    payload = _workbook_bytes()
    result = adapt_v13_workbook(payload, filename="PROCUREMENT_COPILOT_UPLOAD.xlsx")

    assert result.mode == "FULL_SOURCING_REVIEW"
    assert result.schema_version == "1.3.0"
    assert result.alias_registry_version == "1.3.0"
    assert result.upload_file_hash_sha256 == sha256(payload).hexdigest()
    assert result.source_file_hash_sha256 == "a" * 64
    assert len(result.rfq_quotes) == 2
    assert len(result.po_history) == 1
    assert result.rfq_quotes[0].canonical_values["RFQ_NUMBER"] == "0010000001"
    assert result.rfq_quotes[0].canonical_values["BASE_UNIT_PRICE"].as_tuple().exponent < 1
    assert result.rfq_quotes[0].normalized_values == {}
    assert result.rfq_quotes[0].provenance.upload_file_hash_sha256 == sha256(payload).hexdigest()
    assert not result.has_fatal


def test_quick_mode_is_detected_without_history():
    result = adapt_v13_workbook(_workbook_bytes(include_history=False), filename="quick.xlsx")
    assert result.mode == "QUICK_RFQ"
    assert result.po_history == ()
    assert not any(item.code == "PO_HISTORY_UNAVAILABLE" for item in result.findings)


def test_mode_is_inferred_when_metadata_is_absent():
    result = adapt_v13_workbook(
        _workbook_bytes(include_history=False, include_metadata=False),
        filename="quick.xlsx",
    )
    assert result.mode == "QUICK_RFQ"
    assert result.upload_metadata is None


def test_multiple_events_require_explicit_selection():
    payload = _workbook_bytes(second_event=True)
    result = adapt_v13_workbook(payload, filename="multi.xlsx")
    assert result.available_sourcing_event_ids == ("EVT-001", "EVT-002")
    assert any(item.code == "SOURCING_EVENT_SELECTION_REQUIRED" for item in result.findings)

    selected = adapt_v13_workbook(payload, filename="multi.xlsx", selected_sourcing_event_id="EVT-002")
    assert {item.canonical_values["SOURCING_EVENT_ID"] for item in selected.rfq_quotes} == {"EVT-002"}
    assert not any(item.code == "SOURCING_EVENT_SELECTION_REQUIRED" for item in selected.findings)


def test_invalid_event_selection_is_fatal():
    result = adapt_v13_workbook(_workbook_bytes(), filename="event.xlsx", selected_sourcing_event_id="MISSING")
    assert any(item.code == "SOURCING_EVENT_SELECTION_INVALID" and item.severity == "Fatal" for item in result.findings)


def test_formula_in_price_is_rejected_without_using_cached_value():
    result = adapt_v13_workbook(_workbook_bytes(formula_price=True), filename="formula.xlsx")
    assert any(item.code == "FORMULA_CELL_REJECTED" and item.field_name == "BASE_UNIT_PRICE" for item in result.findings)
    assert result.rfq_quotes[0].canonical_values.get("BASE_UNIT_PRICE") is None


def test_normalized_high_risk_alias_requires_confirmation():
    payload = _workbook_bytes(alias_header=True)
    result = adapt_v13_workbook(payload, filename="alias.xlsx")
    review = next(item for item in result.mapping_reviews if item.source_header == "RFQ-Number")
    assert review.canonical_field == "RFQ_NUMBER"
    assert review.confidence_class == "NORMALIZED_APPROVED"
    assert review.requires_confirmation
    assert any(item.code == "HIGH_RISK_MAPPING_CONFIRMATION_REQUIRED" for item in result.findings)

    confirmed = adapt_v13_workbook(
        payload,
        filename="alias.xlsx",
        confirmed_mappings={("RFQ_QUOTES", "RFQ-Number", "RFQ_NUMBER")},
    )
    confirmed_review = next(item for item in confirmed.mapping_reviews if item.source_header == "RFQ-Number")
    assert not confirmed_review.requires_confirmation
    assert not any(item.code == "HIGH_RISK_MAPPING_CONFIRMATION_REQUIRED" and item.field_name == "RFQ_NUMBER" for item in confirmed.findings)


def test_latest_quotation_version_is_active_and_prior_version_retained():
    wb = Workbook()
    ws = wb.active
    ws.title = "RFQ_QUOTES"
    headers = _required_headers("RFQQuoteRow")
    ws.append(headers)
    _append_row(ws, headers, supplier="0000100001", version=1)
    _append_row(ws, headers, supplier="0000100001", version=2)
    _append_row(ws, headers, supplier="0000100002", version=1)
    stream = BytesIO()
    wb.save(stream)
    wb.close()

    result = adapt_v13_workbook(stream.getvalue(), filename="versions.xlsx")
    supplier_one = [item for item in result.rfq_quotes if item.canonical_values["SUPPLIER_ID"] == "0000100001"]
    assert len(supplier_one) == 2
    assert [item.canonical_values["QUOTATION_VERSION"] for item in supplier_one if item.active] == [2]


def test_renamed_non_xlsx_payload_is_rejected_by_existing_safety_loader():
    with pytest.raises(WorkbookAdapterError, match="valid XLSX package"):
        adapt_v13_workbook(b"not an xlsx", filename="renamed.xlsx")


def test_alias_contract_is_versioned_and_collective_number_is_not_event_alias():
    registry = json.loads(Path(ALIAS_PATH).read_text(encoding="utf-8"))
    assert registry["registry_version"] == "1.3.0"
    assert "Collective Number" not in registry["sheets"]["RFQ_QUOTES"]["SOURCING_EVENT_ID"]
    assert "Collective Number" in registry["sheets"]["RFQ_QUOTES"]["COLLECTIVE_NUMBER"]
