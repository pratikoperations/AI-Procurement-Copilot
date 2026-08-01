from decimal import Decimal

import pytest

from modules.calculation_reconciliation_gate3 import ToleranceRule, reconcile_trace
from modules.calculation_trace import build_trace
from modules.reconciliation_coverage import RECONCILIATION_COVERAGE


def _trace(raw_output, *, calculation_id="KRF-001", formula_id="F-RM-SHOULDCOST", formula_version="1.0", category="Kraft Paper", inputs=None, blocking=None, impact=None):
    return build_trace(
        calculation_id=calculation_id,
        formula_id=formula_id,
        formula_version=formula_version,
        category=category,
        input_snapshot=inputs or {"volume": 1000},
        raw_output=raw_output,
        blocking_rule_record=blocking,
        recommendation_impact=impact,
        configuration_versions={},
    )


def test_cross_category_coverage_matrix_is_complete():
    domains = {(item.domain, item.category) for item in RECONCILIATION_COVERAGE}
    required = {
        ("should_cost", "PET Resin"), ("should_cost", "Kraft Paper"),
        ("should_cost", "Corrugated Board"), ("should_cost", "Flexible Laminates"),
        ("should_cost", "Steel"), ("tco", "Packaging"), ("tco", "Raw materials"),
        ("risk", "Generic"), ("risk", "Flexible Laminates"), ("risk", "Steel"),
        ("scoring", "Packaging and Raw materials"), ("scoring", "Steel"),
        ("performance", "Packaging and Raw materials"), ("esg", "Packaging and Raw materials"),
        ("technical_eligibility", "Cross-category"), ("recommendation_eligibility", "All"),
        ("allocation", "Generic"), ("scenario", "Generic"),
        ("scenario", "Flexible Laminates"), ("scenario", "Steel"),
        ("export", "All"),
    }
    assert required <= domains
    assert len({item.coverage_id for item in RECONCILIATION_COVERAGE}) == len(RECONCILIATION_COVERAGE)


@pytest.mark.parametrize("coverage", RECONCILIATION_COVERAGE)
def test_every_registered_coverage_has_authoritative_source(coverage):
    assert coverage.source_module.startswith("modules/")
    assert coverage.source_function
    assert coverage.calculation_id
    assert coverage.formula_id


def test_exact_match_is_clear_and_deterministic():
    output = {"target_cost": 1.25, "unit": "USD/kg"}
    trace = _trace(output)
    first = reconcile_trace(
        trace=trace,
        authoritative_service="calculate_raw_material_should_cost",
        authoritative_output=output,
        calculation_id="KRF-001",
        formula_id="F-RM-SHOULDCOST",
        formula_version="1.0",
        compared_fields=("target_cost", "unit"),
        repeated_trace_id=trace.trace_id,
    )
    second = reconcile_trace(
        trace=trace,
        authoritative_service="calculate_raw_material_should_cost",
        authoritative_output=output,
        calculation_id="KRF-001",
        formula_id="F-RM-SHOULDCOST",
        formula_version="1.0",
        compared_fields=("target_cost", "unit"),
        repeated_trace_id=trace.trace_id,
    )
    assert first.classification == "exact_match"
    assert first.blocking_status == "clear"
    assert first.reconciliation_id == second.reconciliation_id
    assert first.human_review_status == "required"


def test_rounding_only_difference_requires_explicit_field_rule():
    trace = _trace({"target_cost": 1.2345})
    result = reconcile_trace(
        trace=trace,
        authoritative_service="calculate_raw_material_should_cost",
        authoritative_output={"target_cost": 1.2344},
        calculation_id="KRF-001",
        formula_id="F-RM-SHOULDCOST",
        formula_version="1.0",
        compared_fields=("target_cost",),
        tolerance_rules=(ToleranceRule("TOL-COST-001", "1.0", "target_cost", Decimal("0.0002")),),
    )
    assert result.classification == "rounding_only_difference"
    assert result.blocking_status == "review_required"
    assert result.tolerated_differences[0]["tolerance_rule_id"] == "TOL-COST-001"


def test_material_output_mismatch_fails_closed():
    trace = _trace({"target_cost": 1.40})
    result = reconcile_trace(
        trace=trace,
        authoritative_service="calculate_raw_material_should_cost",
        authoritative_output={"target_cost": 1.20},
        calculation_id="KRF-001",
        formula_id="F-RM-SHOULDCOST",
        formula_version="1.0",
        compared_fields=("target_cost",),
    )
    assert result.blocking_status == "blocked"
    assert result.classification == "existing_business_logic_inconsistency"


def test_metadata_mismatch_fails_closed():
    trace = _trace({"value": 1})
    result = reconcile_trace(
        trace=trace,
        authoritative_service="service",
        authoritative_output={"value": 1},
        calculation_id="PET-001",
        formula_id="F-RM-SHOULDCOST",
        formula_version="1.0",
        compared_fields=("value",),
    )
    assert result.blocking_status == "blocked"
    assert result.classification == "metadata_defect"


def test_blocker_and_recommendation_mismatch_fail_closed():
    trace = _trace({"status": "Blocked"}, calculation_id="ELG-001", formula_id="F-ELIGIBILITY", category="All", blocking={"status": "Blocked"}, impact="Blocked")
    result = reconcile_trace(
        trace=trace,
        authoritative_service="evaluate_recommendation_eligibility",
        authoritative_output={"status": "Blocked"},
        calculation_id="ELG-001",
        formula_id="F-ELIGIBILITY",
        formula_version="1.0",
        compared_fields=("status",),
        expected_blocking_rule={"status": "Eligible"},
        expected_recommendation_impact="Eligible",
    )
    assert result.blocking_status == "blocked"
    assert {item["field_path"] for item in result.mismatches} == {"blocking_rule_record", "recommendation_impact"}


def test_repeated_trace_identity_mismatch_fails_closed():
    trace = _trace({"value": 1})
    result = reconcile_trace(
        trace=trace,
        authoritative_service="service",
        authoritative_output={"value": 1},
        calculation_id="KRF-001",
        formula_id="F-RM-SHOULDCOST",
        formula_version="1.0",
        compared_fields=("value",),
        repeated_trace_id="trace_changed",
    )
    assert result.blocking_status == "blocked"
    assert any(item["field_path"] == "trace_id" for item in result.mismatches)


def test_unavailable_intermediate_is_disclosed_not_reconstructed():
    trace = _trace({"target_cost": 1.25})
    result = reconcile_trace(
        trace=trace,
        authoritative_service="calculate_raw_material_should_cost",
        authoritative_output={"target_cost": 1.25},
        calculation_id="KRF-001",
        formula_id="F-RM-SHOULDCOST",
        formula_version="1.0",
        compared_fields=("target_cost",),
        unavailable_evidence=("yield_loss_intermediate",),
    )
    assert result.classification == "unavailable_authoritative_intermediate"
    assert result.unavailable_evidence == ("yield_loss_intermediate",)


def test_changed_governed_input_or_version_changes_trace_id():
    first = _trace({"value": 1}, inputs={"volume": 1000})
    changed_input = _trace({"value": 1}, inputs={"volume": 1001})
    changed_version = _trace({"value": 1}, formula_version="1.1")
    assert first.trace_id != changed_input.trace_id
    assert first.trace_id != changed_version.trace_id


def test_authoritative_output_object_is_not_mutated():
    output = {"nested": {"value": 1}}
    trace = _trace(output)
    reconcile_trace(
        trace=trace,
        authoritative_service="service",
        authoritative_output=output,
        calculation_id="KRF-001",
        formula_id="F-RM-SHOULDCOST",
        formula_version="1.0",
        compared_fields=("nested.value",),
    )
    assert output == {"nested": {"value": 1}}
