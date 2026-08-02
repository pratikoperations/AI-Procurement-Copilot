"""Feasibility tests for exactly-K governed multi-supplier portfolios."""

from copy import deepcopy
import math

import pandas as pd
import pytest

from modules.allocation_contract import FeasibilityStatus, MultiSupplierAllocationRequest
from modules.allocation_feasibility import evaluate_allocation_feasibility


def make_request(**overrides):
    values = {
        "annual_volume": 1000,
        "annual_volume_unit": "kg",
        "required_awardee_count": 3,
        "minimum_awarded_share_pct": 10,
        "maximum_supplier_share_pct": 60,
        "minimum_continuity_share_pct": 15,
        "minimum_risk_score": 55,
        "minimum_esg_score": 50,
        "capacity_utilization_ceiling_pct": 100,
        "category": "Packaging Procurement",
        "commodity": "Corrugated Board",
        "comparison_currency": "USD",
    }
    values.update(overrides)
    return MultiSupplierAllocationRequest(**values)


def supplier(name, capacity=600, eligible=True, risk=75, esg=70, tco=1.0, score=80):
    return {
        "Supplier": name,
        "technical_eligible": eligible,
        "adjusted_tco_unit_usd": tco,
        "total_score": score,
        "risk_score": risk,
        "performance_score": 85,
        "esg_score": esg,
        "Supplier Capacity": capacity,
        "technical_ineligibility_reasons": "" if eligible else "Technical requirement failed",
    }


def six_bidders():
    return [
        supplier("Vendor A", 500, score=95),
        supplier("Vendor B", 450, score=90),
        supplier("Vendor C", 400, score=85),
        supplier("Vendor D", 350, score=80),
        supplier("Vendor E", 300, score=75),
        supplier("Vendor F", 700, eligible=False, score=70),
    ]


def test_six_bidders_five_eligible_k3_is_feasible():
    result = evaluate_allocation_feasibility(make_request(), six_bidders())
    assert result.status_code is FeasibilityStatus.FEASIBLE
    assert result.eligible_supplier_count == 5
    assert result.required_awardee_count == 3
    assert result.feasible_supplier_combinations
    assert all(len(item) == 3 for item in result.feasible_supplier_combinations)


@pytest.mark.parametrize(
    ("k", "maximum", "capacities"),
    [
        (1, 100, [1000]),
        (2, 70, [600, 600]),
        (3, 60, [500, 400, 300]),
    ],
)
def test_k1_k2_k3_valid_cases(k, maximum, capacities):
    records = [supplier(f"Vendor {index}", capacity) for index, capacity in enumerate(capacities, 1)]
    request = make_request(required_awardee_count=k, maximum_supplier_share_pct=maximum)
    result = evaluate_allocation_feasibility(request, records)
    assert result.feasible is True
    assert result.status_code is FeasibilityStatus.FEASIBLE


def test_k_greater_than_eligible_count_is_blocked():
    request = make_request(required_awardee_count=4)
    result = evaluate_allocation_feasibility(request, six_bidders()[:3])
    assert result.status_code is FeasibilityStatus.INSUFFICIENT_ELIGIBLE_SUPPLIERS


def test_minimum_share_times_k_above_100_is_blocked():
    result = evaluate_allocation_feasibility(
        make_request(minimum_awarded_share_pct=40),
        six_bidders(),
    )
    assert result.status_code is FeasibilityStatus.SHARE_CONSTRAINT_CONFLICT


def test_maximum_share_times_k_below_100_is_blocked():
    result = evaluate_allocation_feasibility(
        make_request(maximum_supplier_share_pct=30),
        six_bidders(),
    )
    assert result.status_code is FeasibilityStatus.SHARE_CONSTRAINT_CONFLICT


@pytest.mark.parametrize("capacity", [None, 0, -10, math.nan, math.inf, "unknown"])
def test_missing_zero_negative_or_non_finite_capacity_is_explicit(capacity):
    records = [supplier("Vendor A", capacity), supplier("Vendor B", 600), supplier("Vendor C", 600)]
    result = evaluate_allocation_feasibility(make_request(), records)
    assert result.status_code is FeasibilityStatus.MISSING_CAPACITY_EVIDENCE
    assert result.feasible is False


def test_capacity_utilization_ceiling_reduces_maximum_feasible_share():
    request = make_request(capacity_utilization_ceiling_pct=50)
    records = [supplier("Vendor A", 1000), supplier("Vendor B", 1000), supplier("Vendor C", 1000)]
    result = evaluate_allocation_feasibility(request, records)
    assert result.maximum_feasible_share_by_supplier["vendor a"] == pytest.approx(50)
    assert result.feasible is True


def test_required_supplier_is_present_in_every_feasible_combination():
    request = make_request(required_supplier_ids=("Vendor E",))
    result = evaluate_allocation_feasibility(request, six_bidders())
    assert result.feasible is True
    assert all("vendor e" in item for item in result.feasible_supplier_combinations)


def test_required_supplier_missing_is_blocked():
    result = evaluate_allocation_feasibility(
        make_request(required_supplier_ids=("Unknown Vendor",)),
        six_bidders(),
    )
    assert result.status_code is FeasibilityStatus.REQUIRED_SUPPLIER_MISSING


def test_required_supplier_ineligible_is_blocked():
    result = evaluate_allocation_feasibility(
        make_request(required_supplier_ids=("Vendor F",)),
        six_bidders(),
    )
    assert result.status_code is FeasibilityStatus.REQUIRED_SUPPLIER_INELIGIBLE


def test_required_and_excluded_conflict_is_blocked():
    request = make_request(required_supplier_ids=("Vendor A",), excluded_supplier_ids=("vendor a",))
    result = evaluate_allocation_feasibility(request, six_bidders())
    assert result.status_code is FeasibilityStatus.REQUIRED_EXCLUDED_CONFLICT


def test_excluded_supplier_never_enters_feasible_combination():
    result = evaluate_allocation_feasibility(
        make_request(excluded_supplier_ids=("Vendor A",)),
        six_bidders(),
    )
    assert result.feasible is True
    assert all("vendor a" not in item for item in result.feasible_supplier_combinations)


def test_fewer_than_k_suppliers_supporting_minimum_share_is_blocked():
    records = [supplier("Vendor A", 500), supplier("Vendor B", 500), supplier("Vendor C", 50)]
    result = evaluate_allocation_feasibility(
        make_request(minimum_awarded_share_pct=10),
        records,
    )
    assert result.status_code is FeasibilityStatus.INSUFFICIENT_CAPACITY


def test_combined_capacity_below_demand_is_blocked():
    records = [supplier("Vendor A", 300), supplier("Vendor B", 300), supplier("Vendor C", 300)]
    result = evaluate_allocation_feasibility(make_request(), records)
    assert result.status_code is FeasibilityStatus.INSUFFICIENT_CAPACITY


def test_exact_boundary_capacity_equal_to_demand_is_feasible():
    request = make_request(required_awardee_count=2, maximum_supplier_share_pct=60)
    records = [supplier("Vendor A", 500), supplier("Vendor B", 500)]
    result = evaluate_allocation_feasibility(request, records)
    assert result.status_code is FeasibilityStatus.FEASIBLE
    assert result.maximum_feasible_share_by_supplier == {"vendor a": 50.0, "vendor b": 50.0}


def test_results_are_deterministic_under_repeated_execution():
    request = make_request()
    first = evaluate_allocation_feasibility(request, six_bidders())
    second = evaluate_allocation_feasibility(request, six_bidders())
    assert first.to_json() == second.to_json()


def test_results_are_deterministic_when_input_row_order_changes():
    request = make_request()
    first = evaluate_allocation_feasibility(request, six_bidders())
    second = evaluate_allocation_feasibility(request, list(reversed(six_bidders())))
    assert first.to_json() == second.to_json()


def test_source_records_are_not_mutated():
    records = six_bidders()
    original = deepcopy(records)
    evaluate_allocation_feasibility(make_request(), records)
    assert records == original


def test_source_dataframe_is_not_mutated():
    frame = pd.DataFrame(six_bidders())
    original = frame.copy(deep=True)
    evaluate_allocation_feasibility(make_request(), frame)
    pd.testing.assert_frame_equal(frame, original)


def test_human_review_is_always_mandatory():
    result = evaluate_allocation_feasibility(make_request(), six_bidders())
    assert result.human_review_required is True
    assert any("Human procurement approval" in item for item in result.warnings)


def test_duplicate_supplier_identifiers_are_invalid():
    records = [supplier("Vendor A", 600), supplier(" vendor   a ", 600), supplier("Vendor B", 600)]
    result = evaluate_allocation_feasibility(make_request(), records)
    assert result.status_code is FeasibilityStatus.INVALID_REQUEST


def test_risk_and_esg_thresholds_define_commercial_eligibility():
    records = six_bidders()
    records[0]["risk_score"] = 10
    records[1]["esg_score"] = 10
    result = evaluate_allocation_feasibility(make_request(required_awardee_count=4), records)
    assert result.status_code is FeasibilityStatus.INSUFFICIENT_ELIGIBLE_SUPPLIERS


def test_no_capacity_is_inferred_for_missing_values():
    records = six_bidders()
    records[0]["Supplier Capacity"] = None
    result = evaluate_allocation_feasibility(make_request(), records)
    evidence = {item["supplier_id"]: item for item in result.supplier_capacity_evidence}
    assert result.status_code is FeasibilityStatus.MISSING_CAPACITY_EVIDENCE
    assert evidence["vendor a"]["supplier_capacity"] is None
    assert evidence["vendor a"]["capacity_verified"] is False


def test_bounded_enumeration_policy_is_deterministic_and_disclosed():
    records = [supplier(f"Vendor {index:02d}", 500) for index in range(1, 11)]
    request = make_request(required_awardee_count=5, maximum_supplier_share_pct=40)
    result = evaluate_allocation_feasibility(request, records, max_combinations=3)
    assert result.combinations_evaluated == 3
    assert result.combinations_truncated is True
    assert result.enumeration_policy == "bounded_deterministic_enumeration_first_3"


@pytest.mark.parametrize(
    ("category", "commodity"),
    [
        ("Packaging Procurement", "Corrugated Board"),
        ("Packaging Procurement", "PET"),
        ("Packaging Procurement", "Kraft Paper"),
        ("Packaging Procurement", "Flexible Laminates"),
        ("Raw Material Procurement", "Steel"),
        ("Generic Uploaded RFQ", "Client Material"),
    ],
)
def test_common_contract_is_cross_category_without_category_specific_logic(category, commodity):
    request = make_request(category=category, commodity=commodity)
    result = evaluate_allocation_feasibility(request, six_bidders())
    assert result.status_code is FeasibilityStatus.FEASIBLE
    assert result.contract_version == "AIPC-MULTI-ALLOC-1.0"


def test_required_supplier_count_cannot_exceed_k():
    request = make_request(required_awardee_count=2, required_supplier_ids=("Vendor A", "Vendor B", "Vendor C"))
    result = evaluate_allocation_feasibility(request, six_bidders())
    assert result.status_code is FeasibilityStatus.INVALID_REQUEST


def test_invalid_enumeration_bound_is_blocked():
    result = evaluate_allocation_feasibility(make_request(), six_bidders(), max_combinations=0)
    assert result.status_code is FeasibilityStatus.INVALID_REQUEST
