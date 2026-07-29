from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from modules.ranking_input_models import CanonicalFieldEvidenceResult, RankingModeEligibility, RankingScopeMatch
from modules.rfq_analytical_handoff import DATAFRAME_COLUMNS, RANKING_MAPPING, build_analytical_handoff


def _quote(supplier_id: str, row: int):
    values = {
        "SOURCING_EVENT_ID": "EV1", "RFQ_NUMBER": "RFQ1", "RFQ_ITEM": "10",
        "SUPPLIER_ID": supplier_id, "SUPPLIER_NAME": f"Supplier {supplier_id}",
        "QUOTATION_VERSION": 1, "MINIMUM_ORDER_QUANTITY": Decimal("1000"),
        "LEAD_TIME_DAYS": 20, "PAYMENT_DAYS": 45, "INCOTERMS_CODE": "DDP",
    }
    provenance = SimpleNamespace(source_row_id=f"Q{row}", source_row_number=row, upload_file_hash_sha256="a" * 64, alias_registry_version="1.3.1")
    record = SimpleNamespace(canonical_values=values, provenance=provenance)
    normalization = SimpleNamespace(normalized_values={"COMPARISON_CURRENCY": "USD", "NORMALIZED_UNIT_PRICE": Decimal("12.5"), "COMPARISON_UOM": "EA"})
    return SimpleNamespace(record=record, normalization=normalization, eligible_for_analysis=True)


def _adapter(mode="FULL_SOURCING_REVIEW", schema="1.3.1"):
    quotes = (_quote("S1", 2), _quote("S2", 3))
    eligibility = []
    matches = []
    evidence = []
    for index, supplier in enumerate(("S1", "S2"), start=1):
        record_id = f"R{index}"
        eligibility.append(RankingModeEligibility("FULL_SOURCING_REVIEW", "RFQ1", "10", supplier, tuple(RANKING_MAPPING), tuple(RANKING_MAPPING), (), (), "RANKING_REVIEW_COMPLETE", ()))
        matches.append(RankingScopeMatch("RFQ1", "10", supplier, record_id, "MATERIAL_GROUP", 2, date(2026, 6, 30), 1, True, "MATCHED"))
        for field in RANKING_MAPPING:
            evidence.append(CanonicalFieldEvidenceResult(record_id, supplier, field, Decimal("90"), "VALID", "SOURCE_MAPPED", {"source_row_id": f"RS{index}"}, ()))
    return SimpleNamespace(
        upload_metadata={"SCHEMA_VERSION": schema, "UPLOAD_MODE": mode}, mode=mode,
        rfq_quotes=tuple(item.record for item in quotes), ranking_mode_eligibility=tuple(eligibility),
        ranking_scope_matches=tuple(matches), ranking_evidence_results=tuple(evidence), findings=(),
    ), SimpleNamespace(enriched_quotes=quotes, conditional_findings=())


def test_full_review_builds_exact_governed_dataframe_and_digest():
    adapter, orchestration = _adapter()
    result = build_analytical_handoff(adapter, orchestration, selected_sourcing_event_id="EV1", selected_rfq_number="RFQ1", selected_rfq_item="10", evaluation_date=date(2026, 7, 30))
    assert result.eligible
    assert result.digest
    assert tuple(result.dataframe.columns) == DATAFRAME_COLUMNS
    assert result.dataframe.attrs["analytical_currency"] == "USD"
    assert set(result.dataframe["Supplier ID"]) == {"S1", "S2"}
    assert all(result.dataframe[column].notna().all() for column in RANKING_MAPPING.values())


def test_quick_and_v130_are_review_only():
    quick, orchestration = _adapter(mode="QUICK_RFQ")
    assert "FULL_REVIEW_REQUIRED_FOR_ANALYTICAL_HANDOFF" in build_analytical_handoff(quick, orchestration, selected_sourcing_event_id="EV1", selected_rfq_number="RFQ1", selected_rfq_item="10", evaluation_date=date(2026, 7, 30)).blockers
    old, orchestration = _adapter(schema="1.3.0")
    assert "V130_ANALYTICAL_HANDOFF_PROHIBITED" in build_analytical_handoff(old, orchestration, selected_sourcing_event_id="EV1", selected_rfq_number="RFQ1", selected_rfq_item="10", evaluation_date=date(2026, 7, 30)).blockers


def test_supplier_set_mismatch_is_fatal_and_no_dataframe():
    adapter, orchestration = _adapter()
    adapter = SimpleNamespace(**{**adapter.__dict__, "ranking_mode_eligibility": adapter.ranking_mode_eligibility[:1]})
    result = build_analytical_handoff(adapter, orchestration, selected_sourcing_event_id="EV1", selected_rfq_number="RFQ1", selected_rfq_item="10", evaluation_date=date(2026, 7, 30))
    assert not result.eligible
    assert result.dataframe is None
    assert "SUPPLIER_SET_MISMATCH" in result.blockers


def test_digest_changes_when_canonical_ranking_value_changes():
    adapter, orchestration = _adapter()
    first = build_analytical_handoff(adapter, orchestration, selected_sourcing_event_id="EV1", selected_rfq_number="RFQ1", selected_rfq_item="10", evaluation_date=date(2026, 7, 30))
    changed = list(adapter.ranking_evidence_results)
    item = changed[0]
    changed[0] = CanonicalFieldEvidenceResult(item.ranking_record_id, item.supplier_id, item.canonical_field, Decimal("91"), item.canonical_evidence_status, item.value_origin, item.source_reference, item.validation_findings)
    adapter = SimpleNamespace(**{**adapter.__dict__, "ranking_evidence_results": tuple(changed)})
    second = build_analytical_handoff(adapter, orchestration, selected_sourcing_event_id="EV1", selected_rfq_number="RFQ1", selected_rfq_item="10", evaluation_date=date(2026, 7, 30))
    assert first.digest != second.digest
