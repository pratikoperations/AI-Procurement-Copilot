from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pandas as pd

from modules.ranking_input_models import CanonicalFieldEvidenceResult, RankingModeEligibility, RankingScopeMatch
from modules.rfq_analytical_handoff import (
    DATAFRAME_COLUMNS, RANKING_MAPPING, build_analytical_handoff,
    filter_analytical_assumptions, run_engine_stages,
)


def _quote(supplier_id: str, row: int, *, payment_days=45, price="12.5"):
    values = {
        "SOURCING_EVENT_ID": "EV1", "RFQ_NUMBER": "RFQ1", "RFQ_ITEM": "10",
        "SUPPLIER_ID": supplier_id, "SUPPLIER_NAME": f"Supplier {supplier_id}",
        "QUOTATION_VERSION": 1, "MINIMUM_ORDER_QUANTITY": Decimal("1000"),
        "LEAD_TIME_DAYS": 20, "PAYMENT_DAYS": payment_days,
        "PAYMENT_TERMS_CODE": "NET45", "INCOTERMS_CODE": "DDP",
    }
    provenance = SimpleNamespace(source_row_id=f"Q{row}", source_row_number=row, upload_file_hash_sha256="a" * 64, alias_registry_version="1.3.1")
    record = SimpleNamespace(canonical_values=values, provenance=provenance)
    normalization = SimpleNamespace(normalized_values={"COMPARISON_CURRENCY": "USD", "NORMALIZED_UNIT_PRICE": Decimal(price), "COMPARISON_UOM": "EA"})
    return SimpleNamespace(record=record, normalization=normalization, eligible_for_analysis=True)


def _adapter(mode="FULL_SOURCING_REVIEW", schema="1.3.1", *, payment_days=45, first_price="12.5"):
    quotes = (_quote("S1", 2, payment_days=payment_days, price=first_price), _quote("S2", 3, payment_days=payment_days))
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


def _build(adapter, orchestration, assumptions=None):
    return build_analytical_handoff(
        adapter, orchestration, selected_sourcing_event_id="EV1",
        selected_rfq_number="RFQ1", selected_rfq_item="10",
        evaluation_date=date(2026, 7, 30), analytical_assumptions=assumptions,
    )


def test_full_review_builds_exact_governed_dataframe_and_digest():
    adapter, orchestration = _adapter()
    result = _build(adapter, orchestration)
    assert result.eligible and result.digest
    assert tuple(result.dataframe.columns) == DATAFRAME_COLUMNS
    assert result.dataframe.attrs["analytical_currency"] == "USD"
    assert set(result.dataframe["Supplier ID"]) == {"S1", "S2"}
    assert all(result.dataframe[column].notna().all() for column in RANKING_MAPPING.values())
    payment = next(field for field in result.manifest.suppliers[0].fields if field.target_column == "Payment Terms")
    assert payment.source_field == "PAYMENT_DAYS"
    assert payment.transformation == "PAYMENT_DAYS_TO_DISPLAY"


def test_quick_and_v130_are_review_only():
    quick, orchestration = _adapter(mode="QUICK_RFQ")
    assert "FULL_REVIEW_REQUIRED_FOR_ANALYTICAL_HANDOFF" in _build(quick, orchestration).blockers
    old, orchestration = _adapter(schema="1.3.0")
    assert "V130_ANALYTICAL_HANDOFF_PROHIBITED" in _build(old, orchestration).blockers


def test_supplier_set_mismatch_is_fatal_and_no_dataframe():
    adapter, orchestration = _adapter()
    adapter = SimpleNamespace(**{**adapter.__dict__, "ranking_mode_eligibility": adapter.ranking_mode_eligibility[:1]})
    result = _build(adapter, orchestration)
    assert not result.eligible and result.dataframe is None
    assert "SUPPLIER_SET_MISMATCH" in result.blockers


def test_digest_changes_when_canonical_ranking_value_changes():
    adapter, orchestration = _adapter()
    first = _build(adapter, orchestration)
    changed = list(adapter.ranking_evidence_results)
    item = changed[0]
    changed[0] = CanonicalFieldEvidenceResult(item.ranking_record_id, item.supplier_id, item.canonical_field, Decimal("91"), item.canonical_evidence_status, item.value_origin, item.source_reference, item.validation_findings)
    adapter = SimpleNamespace(**{**adapter.__dict__, "ranking_evidence_results": tuple(changed)})
    assert first.digest != _build(adapter, orchestration).digest


def test_display_only_assumptions_do_not_change_digest_but_analytical_values_do():
    adapter, orchestration = _adapter()
    first = _build(adapter, orchestration, {"annual_volume": 1000, "display_currency": "USD", "fx_rate": 83})
    display_changed = _build(adapter, orchestration, {"annual_volume": 1000, "display_currency": "INR", "fx_rate": 90})
    analytical_changed = _build(adapter, orchestration, {"annual_volume": 2000, "display_currency": "INR", "fx_rate": 90})
    assert first.digest == display_changed.digest
    assert first.digest != analytical_changed.digest
    assert "display_currency" not in filter_analytical_assumptions({"display_currency": "INR", "annual_volume": 1})


def test_build_d_normalized_price_change_changes_digest():
    adapter, orchestration = _adapter(first_price="12.5")
    first = _build(adapter, orchestration)
    adapter2, orchestration2 = _adapter(first_price="12.6")
    assert first.digest != _build(adapter2, orchestration2).digest


def test_payment_days_required_and_code_alone_is_blocked():
    adapter, orchestration = _adapter(payment_days=None)
    result = _build(adapter, orchestration)
    assert not result.eligible
    assert "PAYMENT_DAYS_REQUIRED_FOR_HANDOFF" in result.blockers


def _stage_frame():
    return pd.DataFrame({"Supplier ID": ["S1", "S2"], "Value": [1, 2]})


def test_engine_stage_runner_records_all_successes():
    frame = _stage_frame()
    functions = {stage: (lambda outputs, stage=stage: outputs["dataframe"] if stage == "SCORING_TCO" else {"stage": stage}) for stage in (
        "INPUT_VALIDATION", "SCORING_TCO", "SCORED_OUTPUT_VALIDATION", "RECOMMENDATION", "ALLOCATION", "NEGOTIATION"
    )}
    result = run_engine_stages(frame, "digest", functions)
    assert result.completed
    assert all(item.status == "PASSED" for item in result.stages)
    assert all(item.input_digest == "digest" for item in result.stages)


def test_engine_stage_failure_blocks_every_later_stage():
    frame = _stage_frame()
    def fail(_outputs):
        raise RuntimeError("boom")
    functions = {
        "INPUT_VALIDATION": lambda outputs: True,
        "SCORING_TCO": fail,
        "SCORED_OUTPUT_VALIDATION": lambda outputs: True,
        "RECOMMENDATION": lambda outputs: True,
        "ALLOCATION": lambda outputs: True,
        "NEGOTIATION": lambda outputs: True,
    }
    result = run_engine_stages(frame, "digest", functions)
    assert not result.completed
    assert result.stages[1].status == "BLOCKED"
    assert all(item.status == "NOT_STARTED" for item in result.stages[2:])


def test_engine_stage_supplier_mutation_is_blocked():
    frame = _stage_frame()
    mutated = pd.DataFrame({"Supplier ID": ["S1"], "Value": [1]})
    functions = {
        "INPUT_VALIDATION": lambda outputs: True,
        "SCORING_TCO": lambda outputs: mutated,
        "SCORED_OUTPUT_VALIDATION": lambda outputs: True,
        "RECOMMENDATION": lambda outputs: True,
        "ALLOCATION": lambda outputs: True,
        "NEGOTIATION": lambda outputs: True,
    }
    result = run_engine_stages(frame, "digest", functions)
    assert not result.completed
    assert result.stages[1].finding_code == "SCORING_TCO_FAILED"
