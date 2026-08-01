from decimal import Decimal

import pytest

from modules.calculation_reconciliation_gate3 import ToleranceRule, reconcile_trace
from modules.calculation_trace import build_trace
from modules.reconciliation_coverage import RECONCILIATION_COVERAGE, validate_all_coverage_sources, validate_coverage_source, ReconciliationCoverage


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


def _reconcile(trace, authoritative_output, **kwargs):
    return reconcile_trace(
        trace=trace,
        authoritative_service=kwargs.pop("authoritative_service", "service"),
        authoritative_output=authoritative_output,
        calculation_id=kwargs.pop("calculation_id", trace.calculation_id),
        formula_id=kwargs.pop("formula_id", trace.formula_id),
        formula_version=kwargs.pop("formula_version", trace.formula_version),
        **kwargs,
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
    assert validate_coverage_source(coverage)


def test_all_registered_sources_resolve_without_business_execution():
    assert validate_all_coverage_sources() == tuple(item.coverage_id for item in RECONCILIATION_COVERAGE)


def test_nonexistent_registered_module_and_function_fail_closed():
    bad_module = ReconciliationCoverage("BAD-MOD", "x", "x", "x", "x", "modules/not_real.py", "service", "x")
    bad_function = ReconciliationCoverage("BAD-FN", "x", "x", "x", "x", "modules/risk.py", "not_real", "x")
    with pytest.raises((ModuleNotFoundError, ValueError)):
        validate_coverage_source(bad_module)
    with pytest.raises(ValueError):
        validate_coverage_source(bad_function)


def test_exact_match_is_clear_and_deterministic():
    output = {"target_cost": 1.25, "unit": "USD/kg"}
    trace = _trace(output)
    first = _reconcile(trace, output, compared_fields=("target_cost", "unit"), repeated_trace_id=trace.trace_id)
    second = _reconcile(trace, output, compared_fields=("target_cost", "unit"), repeated_trace_id=trace.trace_id)
    assert first.classification == "exact_match"
    assert first.blocking_status == "clear"
    assert first.reconciliation_id == second.reconciliation_id
    assert first.human_review_status == "required"


def test_rounding_only_difference_requires_explicit_field_rule():
    trace = _trace({"target_cost": 1.2345})
    result = _reconcile(
        trace, {"target_cost": 1.2344}, compared_fields=("target_cost",),
        tolerance_rules=(ToleranceRule("TOL-COST-001", "1.0", "target_cost", Decimal("0.0002")),),
    )
    assert result.classification == "rounding_only_difference"
    assert result.blocking_status == "review_required"
    assert result.tolerated_differences[0]["tolerance_rule_id"] == "TOL-COST-001"
    assert result.tolerated_differences[0]["tolerance_rule_version"] == "1.0"


@pytest.mark.parametrize("field", [
    "calculation_id", "formula_id", "formula_version", "trace_id", "status",
    "eligibility.status", "blocking_rule_record", "recommendation_impact",
    "allocation_label", "scenario_label", "steel_governance.winner_state",
])
def test_prohibited_tolerance_paths_fail_closed(field):
    with pytest.raises(ValueError):
        ToleranceRule("TOL-X", "1.0", field, Decimal("0.1"))


@pytest.mark.parametrize("rule", [
    ("", "1.0", "value", Decimal("0.1")),
    ("TOL", "", "value", Decimal("0.1")),
    ("TOL", "1.0", "", Decimal("0.1")),
    ("TOL", "1.0", "value", Decimal("NaN")),
    ("TOL", "1.0", "value", Decimal("Infinity")),
])
def test_invalid_tolerance_metadata_fails_closed(rule):
    with pytest.raises(ValueError):
        ToleranceRule(*rule)


def test_duplicate_rule_ids_and_paths_fail_closed():
    trace = _trace({"value": 1})
    with pytest.raises(ValueError):
        _reconcile(trace, {"value": 1}, compared_fields=("value",), tolerance_rules=(
            ToleranceRule("TOL-1", "1.0", "value", Decimal("0.1")),
            ToleranceRule("TOL-1", "2.0", "other", Decimal("0.1")),
        ))
    with pytest.raises(ValueError):
        _reconcile(trace, {"value": 1}, compared_fields=("value",), tolerance_rules=(
            ToleranceRule("TOL-1", "1.0", "value", Decimal("0.1")),
            ToleranceRule("TOL-2", "1.0", "value", Decimal("0.2")),
        ))


def test_comparison_contract_changes_reconciliation_identity():
    trace = _trace({"value": 1, "other": 2})
    first = _reconcile(trace, trace.raw_output, compared_fields=("value",), tolerance_rules=(ToleranceRule("T", "1.0", "value", Decimal("0")),))
    changed_version = _reconcile(trace, trace.raw_output, compared_fields=("value",), tolerance_rules=(ToleranceRule("T", "1.1", "value", Decimal("0")),))
    changed_fields = _reconcile(trace, trace.raw_output, compared_fields=("other",))
    assert first.reconciliation_id != changed_version.reconciliation_id
    assert first.reconciliation_id != changed_fields.reconciliation_id


@pytest.mark.parametrize(("authoritative", "traced", "expected", "actual"), [
    ({}, {"value": 1}, "missing", "present"),
    ({"value": 1}, {}, "present", "missing"),
    ({}, {}, "missing", "missing"),
])
def test_missing_path_diagnostics_are_directional(authoritative, traced, expected, actual):
    result = _reconcile(_trace(traced), authoritative, compared_fields=("value",))
    mismatch = result.mismatches[0]
    assert result.blocking_status == "blocked"
    assert mismatch["authoritative_value"] == expected
    assert mismatch["trace_value"] == actual


def test_material_output_mismatch_fails_closed():
    result = _reconcile(_trace({"target_cost": 1.40}), {"target_cost": 1.20}, compared_fields=("target_cost",))
    assert result.blocking_status == "blocked"
    assert result.classification == "existing_business_logic_inconsistency"


def test_metadata_mismatch_fails_closed():
    result = _reconcile(_trace({"value": 1}), {"value": 1}, calculation_id="PET-001", compared_fields=("value",))
    assert result.blocking_status == "blocked"
    assert result.classification == "metadata_defect"


def test_blocker_and_recommendation_mismatch_fail_closed():
    trace = _trace({"status": "Blocked"}, calculation_id="ELG-001", formula_id="F-ELIGIBILITY", category="All", blocking={"status": "Blocked"}, impact="Blocked")
    result = _reconcile(trace, {"status": "Blocked"}, compared_fields=("status",), expected_blocking_rule={"status": "Eligible"}, expected_recommendation_impact="Eligible")
    assert result.blocking_status == "blocked"
    assert {item["field_path"] for item in result.mismatches} == {"blocking_rule_record", "recommendation_impact"}


def test_repeated_trace_identity_mismatch_fails_closed():
    result = _reconcile(_trace({"value": 1}), {"value": 1}, compared_fields=("value",), repeated_trace_id="trace_changed")
    assert result.blocking_status == "blocked"
    assert any(item["field_path"] == "trace_id" for item in result.mismatches)


def test_unavailable_intermediate_is_disclosed_not_reconstructed():
    result = _reconcile(_trace({"target_cost": 1.25}), {"target_cost": 1.25}, compared_fields=("target_cost",), unavailable_evidence=("yield_loss_intermediate",))
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
    _reconcile(_trace(output), output, compared_fields=("nested.value",))
    assert output == {"nested": {"value": 1}}
