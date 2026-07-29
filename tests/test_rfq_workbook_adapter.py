from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path

from openpyxl import Workbook
import pytest

from modules.rfq_workbook_adapter import ALIAS_PATH, SCHEMA_PATH, WorkbookAdapterError, adapt_v13_workbook


def _schema() -> dict:
    return json.loads(Path(SCHEMA_PATH).read_text(encoding="utf-8"))


def _required(definition: str) -> list[str]:
    return list(_schema()["$defs"][definition]["required"])


def _value(field: str, supplier="0000100001", event="EVT-001", version=1):
    values = {
        "SOURCING_EVENT_ID": event, "RFQ_NUMBER": "0010000001", "RFQ_ITEM": "00010",
        "QUOTATION_VERSION": version, "SUPPLIER_ID": supplier, "SUPPLIER_NAME": f"Supplier {supplier[-1]}",
        "MATERIAL_DESCRIPTION": "Synthetic carton", "MATERIAL_GROUP": "PACK", "PURCHASING_ORG": "1000",
        "REQUESTED_QUANTITY": 1000, "QUOTED_QUANTITY": 1000, "QUOTATION_UOM": "EA",
        "COMPARISON_UOM": "EA", "BASE_UNIT_PRICE": 12.5, "PRICE_UNIT": 1, "CURRENCY": "INR",
        "QUOTATION_DATE": "2026-07-01", "VALIDITY_END_DATE": "2026-12-31", "QUOTATION_STATUS": "VALID",
        "SOURCE_TRANSACTION": "ME49", "SOURCE_FILE_NAME": "synthetic.xlsx",
        "SOURCE_EXTRACTED_AT": "2026-07-29T10:00:00", "SOURCE_ROW_ID": f"RFQ-{supplier}-{version}",
        "PO_NUMBER": "0045000001", "PO_ITEM": "00010", "PO_DATE": "2026-06-01",
        "ORDER_QUANTITY": 1000, "ORDER_UOM": "EA", "NET_PRICE": 12.0, "NET_ORDER_VALUE": 12000,
        "PO_STATUS": "COMPLETE", "DELETION_FLAG": False,
    }
    return values.get(field, "SYNTHETIC")


def _append(ws, headers, *, supplier="0000100001", event="EVT-001", version=1, aliases=None, overrides=None):
    aliases, overrides = aliases or {}, overrides or {}
    ws.append([overrides.get(aliases.get(header, header), _value(aliases.get(header, header), supplier, event, version)) for header in headers])


def _metadata_values(include_history=True, overrides=None):
    headers = ["UPLOAD_ID", "SCHEMA_VERSION", "UPLOAD_MODE", "SOURCE_SYSTEM", "PURCHASING_ORG", "BASE_CURRENCY", "EXTRACTED_AT", "UPLOAD_CREATED_AT", "RFQ_SOURCE_TRANSACTION", "DATA_CLASSIFICATION", "ANONYMIZATION_STATUS", "SOURCE_FILE_HASH_SHA256", "NOTES"]
    values = {
        "UPLOAD_ID": "UP-001", "SCHEMA_VERSION": "1.3.0",
        "UPLOAD_MODE": "FULL_SOURCING_REVIEW" if include_history else "QUICK_RFQ", "SOURCE_SYSTEM": "SAP",
        "PURCHASING_ORG": "1000", "BASE_CURRENCY": "INR", "EXTRACTED_AT": "2026-07-29T10:00:00",
        "UPLOAD_CREATED_AT": "2026-07-29T10:05:00", "RFQ_SOURCE_TRANSACTION": "ME49",
        "DATA_CLASSIFICATION": "SYNTHETIC", "ANONYMIZATION_STATUS": "SYNTHETIC",
        "SOURCE_FILE_HASH_SHA256": "a" * 64, "NOTES": "Upload hash calculated externally.",
    }
    values.update(overrides or {})
    return headers, [values[h] for h in headers]


def _book(*, rows=None, include_history=True, include_metadata=True, second_event=False, exact_alias=False, normalized_alias=False, metadata_overrides=None, extra_metadata=False, empty=False):
    wb = Workbook(); rfq = wb.active; rfq.title = "RFQ_QUOTES"
    headers = _required("RFQQuoteRow"); aliases = {}
    if exact_alias:
        i = headers.index("SUPPLIER_ID"); headers[i] = "Vendor Number"; aliases["Vendor Number"] = "SUPPLIER_ID"
    if normalized_alias:
        i = headers.index("RFQ_NUMBER"); headers[i] = "RFQ-Number"; aliases["RFQ-Number"] = "RFQ_NUMBER"
    rfq.append(headers)
    if not empty:
        rows = rows or [dict(supplier="0000100001"), dict(supplier="0000100002")]
        for spec in rows:
            _append(rfq, headers, aliases=aliases, **spec)
        if second_event:
            _append(rfq, headers, supplier="0000100003", event="EVT-002", aliases=aliases)
            _append(rfq, headers, supplier="0000100004", event="EVT-002", aliases=aliases)
    if include_history:
        po = wb.create_sheet("PO_HISTORY"); po_headers = _required("POHistoryRow"); po.append(po_headers); _append(po, po_headers)
    if include_metadata:
        md = wb.create_sheet("UPLOAD_METADATA"); md_headers, md_values = _metadata_values(include_history, metadata_overrides); md.append(md_headers); md.append(md_values)
        if extra_metadata:
            _, second = _metadata_values(include_history, {"UPLOAD_ID": "UP-002"}); md.append(second)
    stream = BytesIO(); wb.save(stream); wb.close(); return stream.getvalue()


def _formula_book(rows=(2,)):
    payload = _book(); wb = __import__("openpyxl").load_workbook(BytesIO(payload)); ws = wb["RFQ_QUOTES"]
    col = [c.value for c in ws[1]].index("BASE_UNIT_PRICE") + 1
    for row in rows: ws.cell(row=row, column=col, value="=10+2.5")
    stream = BytesIO(); wb.save(stream); wb.close(); return stream.getvalue()


def _duplicate_book(contradictory=False):
    rows = [dict(supplier="0000100001"), dict(supplier="0000100001", overrides={"SOURCE_ROW_ID": "DUP-2", "SOURCE_FILE_NAME": "other.xlsx", "SOURCE_EXTRACTED_AT": "2026-07-29T11:00:00", **({"BASE_UNIT_PRICE": 13.5} if contradictory else {})}), dict(supplier="0000100002")]
    return _book(rows=rows, include_history=False, include_metadata=False)


def test_full_workbook_parses_and_hashes():
    payload = _book(); result = adapt_v13_workbook(payload, filename="PROCUREMENT_COPILOT_UPLOAD.xlsx")
    assert result.mode == "FULL_SOURCING_REVIEW" and result.upload_file_hash_sha256 == sha256(payload).hexdigest()
    assert result.rfq_quotes[0].canonical_values["RFQ_NUMBER"] == "0010000001"
    assert result.rfq_quotes[0].row_valid and result.rfq_quotes[0].eligible_for_analysis


def test_quick_mode_and_inference():
    assert adapt_v13_workbook(_book(include_history=False), filename="q.xlsx").mode == "QUICK_RFQ"
    assert adapt_v13_workbook(_book(include_history=False, include_metadata=False), filename="q.xlsx").mode == "QUICK_RFQ"


def test_multiple_events_require_selection_and_are_ineligible():
    result = adapt_v13_workbook(_book(second_event=True), filename="m.xlsx")
    assert any(f.code == "SOURCING_EVENT_SELECTION_REQUIRED" for f in result.findings)
    assert all(not r.eligible_for_analysis for r in result.rfq_quotes)


def test_selected_event_filters_and_is_eligible():
    result = adapt_v13_workbook(_book(second_event=True), filename="m.xlsx", selected_sourcing_event_id="EVT-002")
    assert {r.canonical_values["SOURCING_EVENT_ID"] for r in result.rfq_quotes} == {"EVT-002"}
    assert all(r.eligible_for_analysis for r in result.rfq_quotes)


def test_invalid_event_selection_is_fatal():
    result = adapt_v13_workbook(_book(), filename="e.xlsx", selected_sourcing_event_id="MISSING")
    assert any(f.code == "SOURCING_EVENT_SELECTION_INVALID" and f.severity == "Fatal" for f in result.findings)


def test_one_formula_row_blocks_supplier_gate():
    result = adapt_v13_workbook(_formula_book((2,)), filename="f.xlsx")
    assert not result.rfq_quotes[0].row_valid
    assert any(f.code == "MINIMUM_SUPPLIER_COUNT_NOT_MET" for f in result.findings)


def test_all_formula_rows_are_fatal():
    result = adapt_v13_workbook(_formula_book((2, 3)), filename="f.xlsx")
    assert any(f.code == "NO_VALID_QUOTATION_RECORDS" and f.severity == "Fatal" for f in result.findings)


def test_three_suppliers_one_blocked_still_passes_supplier_gate():
    rows = [dict(supplier="0000100001"), dict(supplier="0000100002"), dict(supplier="0000100003")]
    payload = _book(rows=rows); wb = __import__("openpyxl").load_workbook(BytesIO(payload)); ws = wb["RFQ_QUOTES"]
    col = [c.value for c in ws[1]].index("BASE_UNIT_PRICE") + 1; ws.cell(row=2, column=col, value="=1")
    stream = BytesIO(); wb.save(stream); wb.close(); result = adapt_v13_workbook(stream.getvalue(), filename="3.xlsx")
    assert sum(r.eligible_for_analysis for r in result.rfq_quotes) == 2
    assert not any(f.code == "MINIMUM_SUPPLIER_COUNT_NOT_MET" for f in result.findings)


def test_latest_valid_version_uses_earlier_when_higher_formula_blocked():
    rows = [dict(supplier="0000100001", version=1), dict(supplier="0000100001", version=2), dict(supplier="0000100002", version=1)]
    payload = _book(rows=rows, include_history=False, include_metadata=False); wb = __import__("openpyxl").load_workbook(BytesIO(payload)); ws = wb["RFQ_QUOTES"]
    col = [c.value for c in ws[1]].index("BASE_UNIT_PRICE") + 1; ws.cell(row=3, column=col, value="=13")
    stream = BytesIO(); wb.save(stream); wb.close(); result = adapt_v13_workbook(stream.getvalue(), filename="v.xlsx")
    s1 = [r for r in result.rfq_quotes if r.canonical_values["SUPPLIER_ID"] == "0000100001"]
    assert [r.canonical_values["QUOTATION_VERSION"] for r in s1 if r.active] == [1]
    assert next(r for r in s1 if r.canonical_values["QUOTATION_VERSION"] == 2).active is False


def test_latest_valid_version_uses_earlier_when_higher_quantity_invalid():
    rows = [dict(supplier="0000100001", version=1), dict(supplier="0000100001", version=2, overrides={"REQUESTED_QUANTITY": 0}), dict(supplier="0000100002", version=1)]
    result = adapt_v13_workbook(_book(rows=rows, include_history=False, include_metadata=False), filename="v.xlsx")
    assert [r.canonical_values["QUOTATION_VERSION"] for r in result.rfq_quotes if r.canonical_values["SUPPLIER_ID"] == "0000100001" and r.active] == [1]


def test_all_versions_invalid_contribute_no_active_quote():
    rows = [dict(supplier="0000100001", version=1, overrides={"REQUESTED_QUANTITY": 0}), dict(supplier="0000100001", version=2, overrides={"REQUESTED_QUANTITY": 0}), dict(supplier="0000100002", version=1)]
    result = adapt_v13_workbook(_book(rows=rows, include_history=False, include_metadata=False), filename="v.xlsx")
    assert not any(r.active for r in result.rfq_quotes if r.canonical_values["SUPPLIER_ID"] == "0000100001")


def test_duplicate_highest_valid_version_blocks_group():
    rows = [dict(supplier="0000100001", version=2), dict(supplier="0000100001", version=2, overrides={"SOURCE_ROW_ID": "OTHER"}), dict(supplier="0000100002", version=1)]
    result = adapt_v13_workbook(_book(rows=rows, include_history=False, include_metadata=False), filename="v.xlsx")
    assert any(f.code == "QUOTATION_VERSION_CONFLICT" for f in result.findings)
    assert not any(r.eligible_for_analysis for r in result.rfq_quotes if r.canonical_values["SUPPLIER_ID"] == "0000100001")


def test_superseded_version_not_extra_supplier():
    rows = [dict(supplier="0000100001", version=1), dict(supplier="0000100001", version=2)]
    result = adapt_v13_workbook(_book(rows=rows, include_history=False, include_metadata=False), filename="v.xlsx")
    assert sum(r.active for r in result.rfq_quotes) == 1
    assert any(f.code == "MINIMUM_SUPPLIER_COUNT_NOT_MET" for f in result.findings)


def test_normalized_alias_requires_confirmation():
    payload = _book(normalized_alias=True); result = adapt_v13_workbook(payload, filename="a.xlsx")
    assert all(not r.row_valid for r in result.rfq_quotes)
    confirmed = adapt_v13_workbook(payload, filename="a.xlsx", confirmed_mappings={("RFQ_QUOTES", "RFQ-Number", "RFQ_NUMBER")})
    assert all(r.row_valid for r in confirmed.rfq_quotes)


def test_exact_alias_needs_no_confirmation():
    result = adapt_v13_workbook(_book(exact_alias=True), filename="a.xlsx")
    review = next(r for r in result.mapping_reviews if r.source_header == "Vendor Number")
    assert review.confidence_class == "EXACT_APPROVED" and not review.requires_confirmation


def test_provenance_duplicate_warning_and_business_conflict_fatal():
    warning = adapt_v13_workbook(_duplicate_book(False), filename="d.xlsx")
    fatal = adapt_v13_workbook(_duplicate_book(True), filename="d.xlsx")
    assert any(f.code == "EXACT_DUPLICATE_ROW" for f in warning.findings)
    assert any(f.code == "CONTRADICTORY_DUPLICATE_KEY" and f.severity == "Fatal" for f in fatal.findings)


def test_empty_rfq_is_fatal():
    assert any(f.code == "RFQ_QUOTES_EMPTY" for f in adapt_v13_workbook(_book(empty=True), filename="e.xlsx").findings)


def test_multiple_metadata_rows_are_fatal():
    assert any(f.code == "UPLOAD_METADATA_CARDINALITY_INVALID" for f in adapt_v13_workbook(_book(extra_metadata=True), filename="m.xlsx").findings)


@pytest.mark.parametrize("overrides,code", [
    ({"SOURCE_FILE_HASH_SHA256": "bad"}, "SOURCE_FILE_HASH_INVALID"),
    ({"SCHEMA_VERSION": "1.2.0"}, "SCHEMA_VERSION_UNSUPPORTED"),
    ({"ANONYMIZATION_STATUS": "UNKNOWN"}, "ANONYMIZATION_STATUS_INVALID"),
    ({"BASE_CURRENCY": "inr"}, "CURRENCY_FORMAT_INVALID"),
])
def test_metadata_controls(overrides, code):
    assert any(f.code == code for f in adapt_v13_workbook(_book(metadata_overrides=overrides), filename="m.xlsx").findings)


def test_selected_event_all_blocked_is_fatal():
    payload = _book(second_event=True); wb = __import__("openpyxl").load_workbook(BytesIO(payload)); ws = wb["RFQ_QUOTES"]
    col = [c.value for c in ws[1]].index("BASE_UNIT_PRICE") + 1
    for row in (4, 5): ws.cell(row=row, column=col, value="=1")
    stream = BytesIO(); wb.save(stream); wb.close(); result = adapt_v13_workbook(stream.getvalue(), filename="s.xlsx", selected_sourcing_event_id="EVT-002")
    assert any(f.code == "NO_VALID_SELECTED_EVENT_QUOTATIONS" for f in result.findings)


def test_renamed_payload_rejected():
    with pytest.raises(WorkbookAdapterError, match="valid XLSX package"):
        adapt_v13_workbook(b"not xlsx", filename="renamed.xlsx")


def test_alias_contract_collective_number_control():
    registry = json.loads(Path(ALIAS_PATH).read_text(encoding="utf-8"))
    assert "Collective Number" not in registry["sheets"]["RFQ_QUOTES"]["SOURCING_EVENT_ID"]
    assert "Collective Number" in registry["sheets"]["RFQ_QUOTES"]["COLLECTIVE_NUMBER"]
