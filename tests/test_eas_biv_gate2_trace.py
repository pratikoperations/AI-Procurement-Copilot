"""Gate 2 parameter precedence and normalized trace contracts."""
from dataclasses import asdict
from datetime import date
from decimal import Decimal

import pytest

from modules.calculation_trace import (
    TRACE_CONTRACT_VERSION,
    build_trace,
    deterministic_trace_id,
)
from modules.calculation_trace_adapters import (
    build_recommendation_eligibility_trace,
    build_should_cost_trace,
    build_supplier_score_trace,
)
from modules.parameter_precedence import (
    ParameterDateValidationError,
    ParameterScopeValidationError,
    resolve_parameter,
)
from modules.parameter_profile_records import ParameterProfileRecord


def rec(
    record_id,
    value,
    level,
    *,
    unit="USD/kg",
    category=None,
    supplier=None,
    rfq=None,
    effective=None,
    expiry=None,
    evidence="approved assumption",
    confidence=None,
    version="1.0",
    source_reference=None,
):
    return ParameterProfileRecord(
        record_id,
        "ASM-001",
        value,
        unit,
        unit,
        category,
        supplier,
        rfq,
        level,
        evidence,
        source_reference=source_reference,
        effective_date=effective,
        review_expiry_date=expiry,
        confidence=confidence,
        version=version,
    )


def test_exact_precedence_order_and_order_independence():
    records = [
        rec("g", 1, "global_default"),
        rec("c", 2, "category_default", category="Kraft Paper"),
        rec("s", 3, "supplier_specific", category="Kraft Paper", supplier="A"),
        rec(
            "r",
            4,
            "rfq_scenario_override",
            category="Kraft Paper",
            supplier="A",
            rfq="RFQ-1",
        ),
    ]
    first = resolve_parameter(
        "ASM-001",
        records,
        category="Kraft Paper",
        supplier="A",
        rfq_scenario="RFQ-1",
        expected_unit="USD/kg",
    )
    second = resolve_parameter(
        "ASM-001",
        reversed(records),
        category="Kraft Paper",
        supplier="A",
        rfq_scenario="RFQ-1",
        expected_unit="USD/kg",
    )
    assert first.selected_source_level == "rfq_scenario_override"
    assert first.selected_value == 4
    assert asdict(first) == asdict(second)


def test_supplier_category_and_global_fallbacks():
    records = [
        rec("g", 1, "global_default"),
        rec("c", 2, "category_default", category="Steel"),
        rec("s", 3, "supplier_specific", category="Steel", supplier="A"),
    ]
    assert resolve_parameter(
        "ASM-001", records, category="Steel", supplier="A"
    ).selected_value == 3
    assert resolve_parameter(
        "ASM-001", records, category="Steel", supplier="B"
    ).selected_value == 2
    assert resolve_parameter(
        "ASM-001", records, category="Kraft Paper", supplier="B"
    ).selected_value == 1


@pytest.mark.parametrize(
    "record,field",
    [
        (rec("g", 1, "global_default", category="Steel"), "category"),
        (rec("c", 1, "category_default"), "category"),
        (rec("s", 1, "supplier_specific"), "supplier"),
        (rec("r", 1, "rfq_scenario_override"), "rfq_scenario"),
    ],
)
def test_malformed_source_scope_fails_closed(record, field):
    with pytest.raises(
        ParameterScopeValidationError,
        match=rf"{record.parameter_record_id}.*{record.source_level}.*{field}",
    ):
        resolve_parameter("ASM-001", [record], category="Steel", supplier="A")


def test_same_priority_conflict_fails_closed():
    with pytest.raises(ValueError, match="Conflicting same-priority"):
        resolve_parameter(
            "ASM-001",
            [
                rec("a", 1, "category_default", category="Steel"),
                rec("b", 2, "category_default", category="Steel"),
            ],
            category="Steel",
        )


def test_equivalent_same_priority_duplicate_is_disclosed_deterministically():
    records = [
        rec("b", 1, "category_default", category="Steel"),
        rec("a", 1.0, "category_default", category="Steel"),
    ]
    result = resolve_parameter("ASM-001", records, category="Steel")
    reversed_result = resolve_parameter("ASM-001", reversed(records), category="Steel")
    assert result.selected_source_record_id == "a"
    assert asdict(result) == asdict(reversed_result)
    assert result.rejected_candidates[0]["resolution_reason"] == (
        "duplicate_same_priority_equivalent"
    )
    assert "duplicate" in result.governance_warning.lower()
    assert "b" in result.governance_warning


def test_unit_expiry_future_effective_missing_and_undocumented_disclosure():
    mismatch = resolve_parameter(
        "ASM-001",
        [rec("x", 1, "global_default", unit="kg")],
        expected_unit="USD/kg",
    )
    assert not mismatch.resolved
    assert mismatch.rejected_candidates[0]["resolution_reason"] == "unit_mismatch"

    expired = resolve_parameter(
        "ASM-001",
        [rec("x", 1, "global_default", expiry="2025-01-01")],
        as_of=date(2026, 1, 1),
    )
    assert not expired.resolved
    assert expired.rejected_candidates[0]["resolution_reason"] == "expired"

    future = resolve_parameter(
        "ASM-001",
        [rec("x", 1, "global_default", effective="2027-01-01")],
        as_of=date(2026, 1, 1),
    )
    assert not future.resolved
    assert future.rejected_candidates[0]["resolution_reason"] == "not_yet_effective"

    missing = resolve_parameter("ASM-X", [])
    assert not missing.resolved
    assert missing.governance_warning == "no_applicable_candidate"

    undocumented = resolve_parameter(
        "ASM-001",
        [
            rec(
                "u",
                1,
                "global_default",
                evidence="existing undocumented controlled default",
            )
        ],
    )
    assert "undocumented" in undocumented.governance_warning


@pytest.mark.parametrize("field", ["effective_date", "review_expiry_date"])
def test_invalid_iso_dates_raise_dedicated_validation_error(field):
    kwargs = {"effective": "not-a-date"} if field == "effective_date" else {"expiry": "not-a-date"}
    record = rec("bad-date", 1, "global_default", **kwargs)
    with pytest.raises(
        ParameterDateValidationError,
        match=rf"bad-date.*{field}.*not-a-date",
    ):
        resolve_parameter("ASM-001", [record])


def test_confidence_is_preserved_but_not_used_as_score():
    result = resolve_parameter(
        "ASM-001", [rec("x", 1, "global_default", confidence=0.55)]
    )
    assert result.confidence == 0.55
    assert not hasattr(result, "decision_score")


def test_trace_identity_is_stable_and_sensitive_to_governed_inputs_and_versions():
    base = dict(
        calculation_id="KRF-001",
        formula_id="F-RM-SHOULDCOST",
        formula_version="1.0",
        category="Kraft Paper",
        input_snapshot={"gsm": 150, "display_timestamp": "x"},
        raw_output={"target": 1.2},
    )
    first = build_trace(**base, timestamp="2026-01-01T00:00:00Z")
    second = build_trace(**base, timestamp="2026-02-01T00:00:00Z")
    assert first.trace_contract_version == TRACE_CONTRACT_VERSION
    assert first.trace_id == second.trace_id
    assert first.trace_id != build_trace(
        **{**base, "input_snapshot": {"gsm": 180}}
    ).trace_id
    assert first.trace_id != build_trace(
        **{**base, "formula_version": "1.1"}
    ).trace_id
    assert first.trace_id != build_trace(
        **base, configuration_versions={"weight_profile": "2.0"}
    ).trace_id


def test_numeric_identity_normalization_and_boolean_separation():
    assert deterministic_trace_id({"value": 1}) == deterministic_trace_id({"value": 1.0})
    assert deterministic_trace_id({"value": 1}) == deterministic_trace_id(
        {"value": Decimal("1.00")}
    )
    assert deterministic_trace_id({"value": 0}) == deterministic_trace_id({"value": -0.0})
    assert deterministic_trace_id({"value": 1.2300}) == deterministic_trace_id(
        {"value": Decimal("1.23")}
    )
    assert deterministic_trace_id({"value": True}) != deterministic_trace_id({"value": 1})
    assert deterministic_trace_id({"value": False}) != deterministic_trace_id({"value": 0})


def test_unsupported_trace_value_type_fails_closed():
    class Unsupported:
        pass

    with pytest.raises(TypeError, match="Unsupported non-deterministic"):
        deterministic_trace_id({"value": Unsupported()})


def test_resolution_order_does_not_change_trace_identity():
    first_resolution = resolve_parameter(
        "ASM-001", [rec("g", 1, "global_default", source_reference="source-a")]
    )
    second_record = ParameterProfileRecord(
        "g-2",
        "ASM-002",
        2,
        "USD/kg",
        "USD/kg",
        None,
        None,
        None,
        "global_default",
        "approved assumption",
        source_reference="source-b",
    )
    second_resolution = resolve_parameter("ASM-002", [second_record])
    base = dict(
        calculation_id="KRF-001",
        formula_id="F-RM-SHOULDCOST",
        formula_version="1.0",
        category="Kraft Paper",
        input_snapshot={"gsm": 150},
        raw_output={"target": 1.2},
    )
    trace_a = build_trace(
        **base, resolutions=(first_resolution, second_resolution)
    )
    trace_b = build_trace(
        **base, resolutions=(second_resolution, first_resolution)
    )
    assert trace_a.trace_id == trace_b.trace_id
    assert trace_a.assumption_ids == ("ASM-001", "ASM-002")


def test_evidence_source_reference_change_alters_trace_identity():
    first = resolve_parameter(
        "ASM-001", [rec("g", 1, "global_default", source_reference="source-a")]
    )
    second = resolve_parameter(
        "ASM-001", [rec("g", 1, "global_default", source_reference="source-b")]
    )
    kwargs = dict(
        calculation_id="KRF-001",
        formula_id="F-RM-SHOULDCOST",
        formula_version="1.0",
        category="Kraft Paper",
        input_snapshot={},
        raw_output={"target": 1},
    )
    assert build_trace(**kwargs, resolutions=(first,)).trace_id != build_trace(
        **kwargs, resolutions=(second,)
    ).trace_id


def test_human_review_cannot_be_disabled():
    with pytest.raises(ValueError, match="require human review"):
        build_trace(
            calculation_id="KRF-001",
            formula_id="F-RM-SHOULDCOST",
            formula_version="1.0",
            category="Kraft Paper",
            input_snapshot={},
            raw_output={"target": 1},
            human_review_status="not_required",
        )


def test_representative_should_cost_traces_preserve_authoritative_output_by_value():
    cases = [
        ("KRF-001", "F-RM-SHOULDCOST", "Kraft Paper"),
        ("LAM-004", "F-C2-SHOULDCOST", "Flexible Laminates"),
        ("STL-003", "F-C3-SHOULDCOST", "Steel"),
    ]
    output = {
        "target_unit_cost_usd": 1.23,
        "components": {"material": 1.0, "margin": 0.23},
    }
    for calculation_id, formula_id, category in cases:
        trace = build_should_cost_trace(
            calculation_id=calculation_id,
            formula_id=formula_id,
            category=category,
            inputs={"category": category},
            authoritative_result=output,
        )
        assert trace.raw_output == output
        assert trace.raw_output is not output
        assert all(
            step["source"] == "authoritative_engine"
            for step in trace.intermediate_steps
        )


def test_generic_scoring_and_recommendation_blocker_traces():
    score_output = {
        "total_score": 82.1,
        "weighted_contribution": {"tco": 32.0},
    }
    score = build_supplier_score_trace(
        inputs={"category": "Packaging"},
        authoritative_result=score_output,
        supplier="A",
    )
    assert score.raw_output == score_output
    assert score.weighted_contribution == {"tco": 32.0}

    blocked_output = {
        "status": "Blocked",
        "reasons": ["technical ineligibility"],
    }
    blocked = build_recommendation_eligibility_trace(
        inputs={"category": "Steel"},
        authoritative_result=blocked_output,
        supplier="B",
    )
    assert blocked.blocking_rule_record["status"] == "Blocked"
    assert blocked.human_review_status == "required"


def test_formula_metadata_is_never_executed_and_non_finite_values_fail():
    trace = build_should_cost_trace(
        calculation_id="KRF-001",
        formula_id="__import__('os').system('false')",
        category="Kraft Paper",
        inputs={},
        authoritative_result={"target": 1},
    )
    assert trace.raw_output == {"target": 1}
    with pytest.raises(ValueError, match="Non-finite"):
        build_trace(
            calculation_id="X",
            formula_id="F",
            formula_version="1",
            category="X",
            input_snapshot={},
            raw_output=float("nan"),
        )
