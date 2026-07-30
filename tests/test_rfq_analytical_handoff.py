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


def _stage_frame(suppliers=("S1", "S2")):
    return pd.DataFrame({"Supplier ID": list(suppliers), "Value": range(1, len(suppliers) + 1)})


def _passing_stage_functions():
    frame = _stage_frame()
    return {
        "INPUT_VALIDATION": lambda outputs: {"is_valid": True},
        "SCORING_TCO": lambda outputs: frame.copy(),
        "SCORED_OUTPUT_VALIDATION": lambda outputs: {"is_valid": True},
        "RECOMMENDATION": lambda outputs: {"recommended": {"Supplier ID": "S1"}},
        "ALLOCATION": lambda outputs: {"allocation_df": frame.copy()},
        "NEGOTIATION": lambda outputs: {"scenario_df": frame.copy()},
    }


def test_engine_stage_runner_records_all_successes_and_exact_digest():
    result = run_engine_stages(_stage_frame(), "digest", _passing_stage_functions())
    assert result.completed
    assert all(item.status == "PASSED" for item in result.stages)
    assert all(item.input_digest == "digest" for item in result.stages)
    assert all(item.supplier_ids == ("S1", "S2") for item in result.stages)


def _assert_stage_failure(stage):
    functions = _passing_stage_functions()

    def fail(_outputs):
        raise RuntimeError("boom")

    functions[stage] = fail
    result = run_engine_stages(_stage_frame(), "digest", functions)
    index = [item.stage for item in result.stages].index(stage)
    assert not result.completed
    assert result.stages[index].status == "BLOCKED"
    assert result.stages[index].finding_code == f"{stage}_FAILED"
    assert all(item.status == "NOT_STARTED" for item in result.stages[index + 1:])
    assert all(item.input_digest == "digest" for item in result.stages)
    return result


def test_recommendation_stage_exception_is_contained():
    _assert_stage_failure("RECOMMENDATION")


def test_allocation_stage_exception_is_contained():
    _assert_stage_failure("ALLOCATION")


def test_negotiation_stage_exception_is_contained():
    _assert_stage_failure("NEGOTIATION")


def _assert_nested_supplier_mismatch(stage, payload):
    functions = _passing_stage_functions()
    functions[stage] = lambda outputs: payload
    result = run_engine_stages(_stage_frame(), "digest", functions)
    index = [item.stage for item in result.stages].index(stage)
    assert not result.completed
    assert result.stages[index].status == "BLOCKED"
    assert result.stages[index].finding_code == f"{stage}_SUPPLIER_SET_MISMATCH"
    assert result.stages[index].input_digest == "digest"
    assert result.stages[index].supplier_ids == ("S1", "S2")
    assert all(item.status == "NOT_STARTED" for item in result.stages[index + 1:])


def test_nested_allocation_dataframe_supplier_removal_is_blocked():
    _assert_nested_supplier_mismatch(
        "ALLOCATION",
        {"allocation_df": _stage_frame(("S1",))},
    )


def test_nested_optimized_allocation_supplier_addition_is_blocked():
    _assert_nested_supplier_mismatch(
        "ALLOCATION",
        {"optimized_allocation": {"allocation_df": _stage_frame(("S1", "S2", "S3"))}},
    )


def test_nested_scenario_dataframe_supplier_removal_is_blocked():
    _assert_nested_supplier_mismatch(
        "NEGOTIATION",
        {"scenario_df": _stage_frame(("S2",))},
    )


def test_valid_nested_supplier_sets_and_supplier_series_pass():
    functions = _passing_stage_functions()
    functions["RECOMMENDATION"] = lambda outputs: {
        "supplier_ids": pd.Series(["S1", "S2"], name="Supplier ID"),
        "metadata": {"message": "valid"},
    }
    functions["ALLOCATION"] = lambda outputs: {
        "allocation_df": _stage_frame(),
        "optimized_allocation": {"allocation_df": _stage_frame()},
    }
    functions["NEGOTIATION"] = lambda outputs: {
        "scenario_df": _stage_frame(),
        "notes": ("no supplier-bearing object here",),
    }
    result = run_engine_stages(_stage_frame(), "digest", functions)
    assert result.completed
    assert all(item.status == "PASSED" for item in result.stages)
