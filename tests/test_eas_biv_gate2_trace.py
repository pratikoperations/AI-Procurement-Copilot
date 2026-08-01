"""Gate 2 parameter precedence and normalized trace contracts."""
from datetime import date

import pytest

from modules.calculation_trace import TRACE_CONTRACT_VERSION, build_trace
from modules.calculation_trace_adapters import (
    build_recommendation_eligibility_trace,
    build_should_cost_trace,
    build_supplier_score_trace,
)
from modules.parameter_precedence import resolve_parameter
from modules.parameter_profile_records import ParameterProfileRecord


def rec(record_id, value, level, *, unit="USD/kg", category=None, supplier=None, rfq=None, expiry=None, evidence="approved assumption", confidence=None, version="1.0"):
    return ParameterProfileRecord(record_id, "ASM-001", value, unit, unit, category, supplier, rfq, level, evidence, review_expiry_date=expiry, confidence=confidence, version=version)


def test_exact_precedence_order_and_order_independence():
    records = [
        rec("g", 1, "global_default"),
        rec("c", 2, "category_default", category="Kraft Paper"),
        rec("s", 3, "supplier_specific", category="Kraft Paper", supplier="A"),
        rec("r", 4, "rfq_scenario_override", category="Kraft Paper", supplier="A", rfq="RFQ-1"),
    ]
    first = resolve_parameter("ASM-001", records, category="Kraft Paper", supplier="A", rfq_scenario="RFQ-1", expected_unit="USD/kg")
    second = resolve_parameter("ASM-001", reversed(records), category="Kraft Paper", supplier="A", rfq_scenario="RFQ-1", expected_unit="USD/kg")
    assert first.selected_source_level == "rfq_scenario_override"
    assert first.selected_value == 4
    assert first.selected_source_record_id == second.selected_source_record_id


def test_supplier_category_and_global_fallbacks():
    records = [rec("g", 1, "global_default"), rec("c", 2, "category_default", category="Steel"), rec("s", 3, "supplier_specific", category="Steel", supplier="A")]
    assert resolve_parameter("ASM-001", records, category="Steel", supplier="A").selected_value == 3
    assert resolve_parameter("ASM-001", records, category="Steel", supplier="B").selected_value == 2
    assert resolve_parameter("ASM-001", records, category="Kraft Paper", supplier="B").selected_value == 1


def test_same_priority_conflict_fails_closed():
    with pytest.raises(ValueError, match="Conflicting same-priority"):
        resolve_parameter("ASM-001", [rec("a", 1, "category_default", category="Steel"), rec("b", 2, "category_default", category="Steel")], category="Steel")


def test_unit_mismatch_expiry_missing_and_undocumented_default_disclosure():
    mismatch = resolve_parameter("ASM-001", [rec("x", 1, "global_default", unit="kg")], expected_unit="USD/kg")
    assert not mismatch.resolved and mismatch.rejected_candidates[0]["resolution_reason"] == "unit_mismatch"
    expired = resolve_parameter("ASM-001", [rec("x", 1, "global_default", expiry="2025-01-01")], as_of=date(2026, 1, 1))
    assert not expired.resolved and expired.rejected_candidates[0]["resolution_reason"] == "expired"
    missing = resolve_parameter("ASM-X", [])
    assert not missing.resolved and missing.governance_warning == "no_applicable_candidate"
    undocumented = resolve_parameter("ASM-001", [rec("u", 1, "global_default", evidence="existing undocumented controlled default")])
    assert "undocumented" in undocumented.governance_warning


def test_confidence_is_preserved_but_not_used_as_score():
    result = resolve_parameter("ASM-001", [rec("x", 1, "global_default", confidence=.55)])
    assert result.confidence == .55
    assert not hasattr(result, "decision_score")


def test_trace_identity_is_stable_and_sensitive_to_governed_inputs_and_versions():
    base = dict(calculation_id="KRF-001", formula_id="F-RM-SHOULDCOST", formula_version="1.0", category="Kraft Paper", input_snapshot={"gsm": 150, "display_timestamp": "x"}, raw_output={"target": 1.2})
    a = build_trace(**base, timestamp="2026-01-01T00:00:00Z")
    b = build_trace(**base, timestamp="2026-02-01T00:00:00Z")
    assert a.trace_contract_version == TRACE_CONTRACT_VERSION
    assert a.trace_id == b.trace_id
    assert a.trace_id != build_trace(**{**base, "input_snapshot": {"gsm": 180}}).trace_id
    assert a.trace_id != build_trace(**{**base, "formula_version": "1.1"}).trace_id
    assert a.trace_id != build_trace(**base, configuration_versions={"weight_profile": "2.0"}).trace_id


def test_representative_should_cost_traces_preserve_authoritative_output_identity_by_value():
    cases = [
        ("KRF-001", "F-RM-SHOULDCOST", "Kraft Paper"),
        ("LAM-004", "F-C2-SHOULDCOST", "Flexible Laminates"),
        ("STL-003", "F-C3-SHOULDCOST", "Steel"),
    ]
    output = {"target_unit_cost_usd": 1.23, "components": {"material": 1.0, "margin": .23}}
    for cid, fid, category in cases:
        trace = build_should_cost_trace(calculation_id=cid, formula_id=fid, category=category, inputs={"category": category}, authoritative_result=output)
        assert trace.raw_output == output
        assert trace.raw_output is not output
        assert all(step["source"] == "authoritative_engine" for step in trace.intermediate_steps)


def test_generic_scoring_and_recommendation_blocker_traces():
    score_output = {"total_score": 82.1, "weighted_contribution": {"tco": 32.0}}
    score = build_supplier_score_trace(inputs={"category": "Packaging"}, authoritative_result=score_output, supplier="A")
    assert score.raw_output == score_output
    assert score.weighted_contribution == {"tco": 32.0}
    blocked_output = {"status": "Blocked", "reasons": ["technical ineligibility"]}
    blocked = build_recommendation_eligibility_trace(inputs={"category": "Steel"}, authoritative_result=blocked_output, supplier="B")
    assert blocked.blocking_rule_record["status"] == "Blocked"
    assert blocked.human_review_status == "required"


def test_formula_metadata_is_never_executed_and_non_finite_values_fail():
    trace = build_should_cost_trace(calculation_id="KRF-001", formula_id="__import__('os').system('false')", category="Kraft Paper", inputs={}, authoritative_result={"target": 1})
    assert trace.raw_output == {"target": 1}
    with pytest.raises(ValueError, match="Non-finite"):
        build_trace(calculation_id="X", formula_id="F", formula_version="1", category="X", input_snapshot={}, raw_output=float("nan"))
