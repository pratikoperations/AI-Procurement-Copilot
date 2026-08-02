from __future__ import annotations

import json
import math

import pandas as pd
import pytest

import modules.multi_supplier_allocation_route as route_module
from modules.allocation_contract import FeasibilityStatus, MultiSupplierFeasibilityResult
from modules.multi_supplier_allocation_route import (
    PARTIAL_EVIDENCE_LABEL,
    ROUTE_VERSION,
    RouteStatus,
    run_multi_supplier_allocation_route,
)


RISK_TEST_MAP = {
    "TR-001": "single canonical route and unchanged Gate 2 result",
    "TR-002": "legacy allocation functions are never invoked",
    "TR-003": "ineligible suppliers receive no allocation",
    "TR-004": "missing or ambiguous eligibility blocks",
    "TR-005": "missing capacity blocks without annual-volume fallback",
    "TR-008": "adapter, feasibility and engine responsibilities remain separate",
    "TR-009": "exactly-K and 100% reconciliation survive the route",
    "TR-011": "infeasible and indeterminate states contain no recommendation",
    "TR-012": "partial evidence and exact label survive late adapter failure",
    "TR-013": "evidence origin survives the route",
    "TR-017": "human procurement review is mandatory for every state",
    "TR-022": "category-specific evidence survives the route",
    "TR-023": "representative categories use the common route",
    "TR-024": "exceptions block without legacy fallback",
}


def controls(**overrides):
    values = {
        "annual_volume": 1000.0,
        "annual_volume_unit": "kg",
        "required_awardee_count": 2,
        "minimum_awarded_share_pct": 10.0,
        "maximum_supplier_share_pct": 60.0,
        "minimum_continuity_share_pct": 20.0,
        "minimum_risk_score": 55.0,
        "minimum_esg_score": 50.0,
        "capacity_utilization_ceiling_pct": 90.0,
        "category": "Raw Material Procurement",
        "commodity": "PET Resin",
        "comparison_currency": "USD",
        "required_supplier_ids": (),
        "excluded_supplier_ids": (),
    }
    values.update(overrides)
    return values


def frame(count=5):
    return pd.DataFrame(
        [
            {
                "Supplier": f"Supplier {chr(65 + index)}",
                "technical_eligible": index != count - 1,
                "adjusted_tco_unit_usd": 1.00 + index * 0.05,
                "total_score": 92.0 - index,
                "risk_score": 82.0 - index,
                "performance_score": 88.0 - index,
                "esg_score": 78.0 - index,
                "Supplier Capacity": 800.0 + index * 25.0,
                "technical_ineligibility_reasons": "Capability gap" if index == count - 1 else "",
            }
            for index in range(count)
        ]
    )


def run(data=None, control_values=None, **kwargs):
    return run_multi_supplier_allocation_route(
        frame() if data is None else data,
        controls() if control_values is None else control_values,
        route_name=kwargs.pop("route_name", "gate-3b1-test-route"),
        source_type=kwargs.pop("source_type", "synthetic_demo"),
        **kwargs,
    )


def indeterminate_result(request):
    return MultiSupplierFeasibilityResult(
        feasible=False,
        status_code=FeasibilityStatus.ENUMERATION_LIMIT_REACHED,
        summary="Feasibility remains indeterminate.",
        eligible_supplier_count=4,
        required_awardee_count=request.required_awardee_count,
        feasible_supplier_count=4,
        supplier_capacity_evidence=(),
        maximum_feasible_share_by_supplier={},
        blocking_reasons=("Deterministic enumeration limit reached",),
        warnings=("Do not treat indeterminate feasibility as infeasible.",),
        feasible_supplier_combinations=(),
        binding_constraints=("enumeration limit",),
        enumeration_policy="bounded_deterministic_enumeration_first_1",
        combinations_evaluated=1,
        combinations_truncated=True,
        decision_complete=False,
    )


def test_required_risk_mapping_is_explicit():
    assert set(RISK_TEST_MAP) == {
        "TR-001", "TR-002", "TR-003", "TR-004", "TR-005", "TR-008", "TR-009",
        "TR-011", "TR-012", "TR-013", "TR-017", "TR-022", "TR-023", "TR-024",
    }


def test_ready_route_invokes_adapter_feasibility_and_engine_once(monkeypatch):
    calls = []
    original_adapter = route_module.build_multi_supplier_allocation_adapter
    original_feasibility = route_module.evaluate_allocation_feasibility
    original_engine = route_module.recommend_multi_supplier_allocation

    def adapter(*args, **kwargs):
        calls.append("adapter")
        return original_adapter(*args, **kwargs)

    def feasibility(*args, **kwargs):
        calls.append("feasibility")
        return original_feasibility(*args, **kwargs)

    def engine(*args, **kwargs):
        calls.append("engine")
        return original_engine(*args, **kwargs)

    monkeypatch.setattr(route_module, "build_multi_supplier_allocation_adapter", adapter)
    monkeypatch.setattr(route_module, "evaluate_allocation_feasibility", feasibility)
    monkeypatch.setattr(route_module, "recommend_multi_supplier_allocation", engine)

    result = run()
    assert calls == ["adapter", "feasibility", "engine"]
    assert result.route_status in {RouteStatus.READY, RouteStatus.WARNING}
    assert result.route_version == ROUTE_VERSION
    assert result.allocation_result is not None


@pytest.mark.parametrize(
    ("column", "expected_status"),
    [
        ("technical_eligible", RouteStatus.BLOCKED_MISSING_ELIGIBILITY),
        ("Supplier Capacity", RouteStatus.BLOCKED_MISSING_CAPACITY),
    ],
)
def test_adapter_block_prevents_feasibility_and_engine(monkeypatch, column, expected_status):
    monkeypatch.setattr(
        route_module,
        "evaluate_allocation_feasibility",
        lambda *args, **kwargs: pytest.fail("feasibility must not run after adapter block"),
    )
    monkeypatch.setattr(
        route_module,
        "recommend_multi_supplier_allocation",
        lambda *args, **kwargs: pytest.fail("engine must not run after adapter block"),
    )
    result = run(frame().drop(columns=[column]))
    assert result.route_status is expected_status
    assert result.feasibility_result is None
    assert result.allocation_result is None
    assert result.legacy_fallback_used is False


def test_ambiguous_eligibility_blocks_without_default():
    data = frame()
    data["technical_eligible"] = data["technical_eligible"].astype(object)
    data.at[0, "technical_eligible"] = "maybe"
    result = run(data)
    assert result.route_status is RouteStatus.BLOCKED_MISSING_ELIGIBILITY
    assert result.allocation_result is None


def test_missing_capacity_never_uses_annual_volume_as_fallback():
    data = frame().drop(columns=["Supplier Capacity"])
    result = run(data)
    assert result.route_status is RouteStatus.BLOCKED_MISSING_CAPACITY
    assert result.allocation_result is None
    assert "capacity" in " ".join(result.blocking_reasons).lower()


def test_infeasible_result_prevents_allocation_recommendation():
    data = frame()
    data["Supplier Capacity"] = 50.0
    result = run(data)
    assert result.route_status is RouteStatus.BLOCKED_INFEASIBLE
    assert result.feasibility_result is not None
    assert result.allocation_result is None
    assert result.legacy_fallback_used is False


def test_indeterminate_feasibility_prevents_engine(monkeypatch):
    def fake_feasibility(request, supplier_inputs, max_combinations=5000):
        return indeterminate_result(request)

    monkeypatch.setattr(route_module, "evaluate_allocation_feasibility", fake_feasibility)
    monkeypatch.setattr(
        route_module,
        "recommend_multi_supplier_allocation",
        lambda *args, **kwargs: pytest.fail("engine must not run for indeterminate feasibility"),
    )
    result = run()
    assert result.route_status is RouteStatus.BLOCKED_INDETERMINATE
    assert result.allocation_result is None


def test_engine_failure_returns_governed_block_without_fallback(monkeypatch):
    def explode(*args, **kwargs):
        raise RuntimeError("engine unavailable")

    monkeypatch.setattr(route_module, "recommend_multi_supplier_allocation", explode)
    result = run()
    assert result.route_status is RouteStatus.BLOCKED_ENGINE_FAILURE
    assert result.allocation_result is None
    assert result.legacy_fallback_used is False
    assert result.blocking_reasons == ("Allocation engine raised RuntimeError",)


def test_adapter_exception_returns_governed_block_without_fallback(monkeypatch):
    class UnprintableFailure(RuntimeError):
        pass

    def explode(*args, **kwargs):
        raise UnprintableFailure()

    monkeypatch.setattr(route_module, "build_multi_supplier_allocation_adapter", explode)
    result = run()
    assert result.route_status is RouteStatus.BLOCKED_ADAPTER_FAILURE
    assert result.adapter_result is None
    assert result.allocation_result is None
    assert result.legacy_fallback_used is False
    assert result.blocking_reasons == ("Adapter raised UnprintableFailure",)


def test_late_adapter_failure_preserves_partial_evidence_and_exact_label():
    data = frame()
    data["Supplier Capacity"] = data["Supplier Capacity"].astype(object)
    data.at[1, "Supplier Capacity"] = None
    result = run(data)
    assert result.route_status is RouteStatus.BLOCKED_MISSING_CAPACITY
    assert result.route_summary == PARTIAL_EVIDENCE_LABEL
    assert PARTIAL_EVIDENCE_LABEL in result.warnings
    assert result.partial_evidence["eligibility_evidence"]
    assert result.partial_evidence["capacity_evidence"]
    assert result.allocation_result is None


def test_legacy_allocation_functions_are_never_called(monkeypatch):
    import modules.allocation as legacy_allocation
    import modules.allocation_optimizer as legacy_optimizer

    monkeypatch.setattr(
        legacy_allocation,
        "recommend_allocation",
        lambda *args, **kwargs: pytest.fail("legacy recommend_allocation must not be invoked"),
    )
    monkeypatch.setattr(
        legacy_optimizer,
        "optimize_allocation",
        lambda *args, **kwargs: pytest.fail("legacy optimize_allocation must not be invoked"),
    )
    result = run()
    assert result.allocation_result is not None
    assert result.legacy_fallback_used is False


@pytest.mark.parametrize("awardee_count", [1, 2, 3])
def test_exactly_k_and_one_hundred_percent_are_preserved(awardee_count):
    maximum_share = 100.0 if awardee_count == 1 else 60.0
    result = run(
        control_values=controls(
            required_awardee_count=awardee_count,
            maximum_supplier_share_pct=maximum_share,
        )
    )
    allocation = result.allocation_result
    assert allocation is not None
    assert len(allocation.selected_supplier_ids) == awardee_count
    assert len([value for value in allocation.allocation_pct_by_supplier.values() if value > 0]) == awardee_count
    assert math.isclose(sum(allocation.allocation_pct_by_supplier.values()), 100.0)


def test_route_preserves_exact_gate_2_result_identity(monkeypatch):
    captured = {}
    original_engine = route_module.recommend_multi_supplier_allocation

    def engine(*args, **kwargs):
        captured["result"] = original_engine(*args, **kwargs)
        return captured["result"]

    monkeypatch.setattr(route_module, "recommend_multi_supplier_allocation", engine)
    result = run()
    assert result.allocation_result is captured["result"]
    assert result.allocation_result.to_json() == captured["result"].to_json()


def test_ineligible_supplier_receives_no_positive_allocation():
    data = frame()
    data.loc[data.index[-1], "adjusted_tco_unit_usd"] = 0.01
    result = run(data)
    allocation = result.allocation_result
    assert allocation is not None
    assert "supplier e" not in allocation.allocation_pct_by_supplier
    assert "supplier e" in allocation.exclusion_reasons


def test_evidence_origin_survives_full_route():
    result = run(source_type="uploaded_rfq")
    assert result.evidence_origin == "supplied"
    assert result.adapter_result is not None
    assert all(item["evidence_origin"] == "supplied" for item in result.adapter_result.capacity_evidence)


def test_category_specific_evidence_survives_full_route():
    data = frame()
    data["GSM"] = 150
    data["Strength Grade"] = "22 BF"
    result = run(data, control_values=controls(commodity="Kraft Paper"))
    assert result.adapter_result is not None
    evidence = result.adapter_result.supplier_inputs[0].category_specific_eligibility_evidence
    assert evidence["GSM"] == 150
    assert evidence["Strength Grade"] == "22 BF"
    assert result.allocation_result is not None


@pytest.mark.parametrize(
    ("category", "commodity", "source_type", "origin"),
    [
        ("Raw Material Procurement", "PET Resin", "synthetic_demo", None),
        ("Packaging Procurement", "Flexible Laminates", "category_adapter", "supplied"),
        ("Raw Material Procurement", "Kraft Paper", "synthetic_demo", None),
        ("Packaging Procurement", "Corrugated Board", "synthetic_demo", None),
    ],
)
def test_representative_categories_use_common_route(category, commodity, source_type, origin):
    data = frame()
    if commodity == "Flexible Laminates":
        data["Laminate Structure"] = "PET / PE"
        data["Application Approval Status"] = "Approved"
    if commodity == "Kraft Paper":
        data["GSM"] = 150
        data["Strength Grade"] = "22 BF"
    result = run(
        data,
        control_values=controls(category=category, commodity=commodity),
        source_type=source_type,
        evidence_origin=origin,
    )
    assert result.allocation_result is not None
    assert result.adapter_result.route_name == "gate-3b1-test-route"


def test_steel_aliases_use_common_route():
    data = frame().drop(columns=["adjusted_tco_unit_usd", "total_score"])
    data["normalized_usd_per_kg"] = [1.1 + index * 0.03 for index in range(len(data))]
    data["governed_total_score"] = [95.0 - index for index in range(len(data))]
    data["governed_rank"] = list(range(1, len(data) + 1))
    result = run(
        data,
        control_values=controls(commodity="Steel"),
        source_type="steel_synthetic",
    )
    assert result.allocation_result is not None
    assert result.evidence_origin == "controlled_synthetic"


def test_shuffled_input_is_deterministic():
    source = frame()
    first = run(source)
    second = run(source.sample(frac=1, random_state=17).reset_index(drop=True))
    assert first.allocation_result is not None
    assert second.allocation_result is not None
    assert first.allocation_result.to_json() == second.allocation_result.to_json()
    assert first.to_json() == second.to_json()


def test_human_review_required_for_ready_blocked_infeasible_and_failure(monkeypatch):
    ready = run()
    missing = run(frame().drop(columns=["technical_eligible"]))
    low_capacity = frame()
    low_capacity["Supplier Capacity"] = 50.0
    infeasible = run(low_capacity)

    monkeypatch.setattr(
        route_module,
        "recommend_multi_supplier_allocation",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("failure")),
    )
    failure = run()
    assert all(item.human_review_required is True for item in (ready, missing, infeasible, failure))


def test_blocked_states_never_contain_allocation_recommendation():
    missing = run(frame().drop(columns=["Supplier Capacity"]))
    low_capacity = frame()
    low_capacity["Supplier Capacity"] = 50.0
    infeasible = run(low_capacity)
    for result in (missing, infeasible):
        assert result.route_status not in {RouteStatus.READY, RouteStatus.WARNING}
        assert result.allocation_result is None


def test_strict_json_contains_no_nan_infinity_or_object_identity():
    result = run()
    payload = result.to_json()
    decoded = json.loads(payload)
    assert decoded["route_version"] == ROUTE_VERSION
    assert "NaN" not in payload
    assert "Infinity" not in payload
    assert "0x" not in payload
    assert "object at" not in payload
    assert decoded["legacy_fallback_used"] is False
    assert decoded["human_review_required"] is True
