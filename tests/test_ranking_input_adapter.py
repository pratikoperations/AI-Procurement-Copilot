from __future__ import annotations

from copy import deepcopy
from datetime import date
from io import BytesIO
import json
from pathlib import Path

from openpyxl import Workbook

from modules.rfq_workbook_adapter import SCHEMA_PATH, adapt_v13_workbook


FIXTURE = Path("tests/fixtures/ranking_input_contract_examples.json")


def _required(definition: str):
    schema = json.loads(Path(SCHEMA_PATH).read_text(encoding="utf-8"))
    return schema["$defs"][definition]["required"]


def _value(field: str, supplier: str):
    values = {
        "SOURCING_EVENT_ID": "EVT-001", "RFQ_NUMBER": "0010000001", "RFQ_ITEM": "00010",
        "QUOTATION_VERSION": 1, "SUPPLIER_ID": supplier, "SUPPLIER_NAME": f"Supplier {supplier[-1]}",
        "MATERIAL_DESCRIPTION": "Carton", "MATERIAL_GROUP": "PACK", "PURCHASING_ORG": "1000",
        "REQUESTED_QUANTITY": 1000, "QUOTED_QUANTITY": 1000, "QUOTATION_UOM": "EA",
        "COMPARISON_UOM": "EA", "BASE_UNIT_PRICE": 12.5, "PRICE_UNIT": 1, "CURRENCY": "INR",
        "QUOTATION_DATE": "2026-07-01", "VALIDITY_END_DATE": "2026-12-31", "QUOTATION_STATUS": "VALID",
        "SOURCE_TRANSACTION": "ME49", "SOURCE_FILE_NAME": "c2.xlsx",
        "SOURCE_EXTRACTED_AT": "2026-07-29T10:00:00", "SOURCE_ROW_ID": f"RFQ-{supplier}",
    }
    return values.get(field, "SYNTHETIC")


def _metadata():
    return {
        "UPLOAD_ID": "UP-C2", "SCHEMA_VERSION": "1.3.1", "UPLOAD_MODE": "QUICK_RFQ",
        "SOURCE_SYSTEM": "SAP", "PURCHASING_ORG": "1000", "BASE_CURRENCY": "INR",
        "EXTRACTED_AT": "2026-07-29T10:00:00", "UPLOAD_CREATED_AT": "2026-07-29T10:05:00",
        "RFQ_SOURCE_TRANSACTION": "ME49", "DATA_CLASSIFICATION": "SYNTHETIC",
        "ANONYMIZATION_STATUS": "SYNTHETIC", "SOURCE_FILE_HASH_SHA256": "a" * 64,
        "NOTES": "Generated C2 fixture",
    }


def _book(alias_otif: bool = False):
    wb = Workbook()
    rfq = wb.active
    rfq.title = "RFQ_QUOTES"
    headers = _required("RFQQuoteRow")
    rfq.append(headers)
    for supplier in ("0000100001", "0000100002"):
        rfq.append([_value(field, supplier) for field in headers])
    md = wb.create_sheet("UPLOAD_METADATA")
    metadata = _metadata()
    md.append(list(metadata))
    md.append(list(metadata.values()))
    ranking = wb.create_sheet("SUPPLIER_RANKING_INPUTS")
    template = json.loads(FIXTURE.read_text(encoding="utf-8"))["valid_quick"]
    rows = []
    for index, supplier in enumerate(("0000100001", "0000100002"), start=1):
        row = deepcopy(template)
        row["RANKING_INPUT_RECORD_ID"] = f"RANK-{index}"
        row["SUPPLIER_ID"] = supplier
        row["SUPPLIER_NAME"] = f"Supplier {index}"
        rows.append(row)
    ranking_headers = list(rows[0])
    if alias_otif:
        ranking_headers[ranking_headers.index("OTIF_PERCENT")] = "OTIF %"
    ranking.append(ranking_headers)
    for row in rows:
        values = []
        for header in ranking_headers:
            canonical = "OTIF_PERCENT" if header == "OTIF %" else header
            value = row.get(canonical)
            values.append(json.dumps(value) if isinstance(value, dict) else value)
        ranking.append(values)
    stream = BytesIO()
    wb.save(stream)
    wb.close()
    return stream.getvalue()


def test_v131_generated_workbook_produces_ranking_review_evidence():
    result = adapt_v13_workbook(_book(), filename="c2.xlsx", evaluation_date=date(2026, 8, 1))
    assert result.schema_version == "1.3.1"
    assert len(result.supplier_ranking_inputs) == 2
    assert len(result.ranking_evidence_results) == 20
    assert len(result.ranking_scope_matches) == 2
    assert all(item.status == "RANKING_REVIEW_COMPLETE" for item in result.ranking_mode_eligibility)
    assert any(item.code == "CANONICAL_RANKING_INPUTS_AVAILABLE_FOR_REVIEW" for item in result.findings)


def test_noncanonical_ranking_alias_requires_bound_confirmation():
    result = adapt_v13_workbook(_book(alias_otif=True), filename="c2.xlsx", evaluation_date=date(2026, 8, 1))
    review = next(item for item in result.mapping_reviews if item.source_header == "OTIF %")
    assert review.requires_confirmation
    assert any(item.code == "RANKING_MAPPING_CONFIRMATION_REQUIRED" for item in result.findings)
