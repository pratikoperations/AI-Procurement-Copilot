"""Tests for the isolated deterministic exactly-K allocation engine."""

from dataclasses import replace
import json

import pytest

from modules.allocation_contract import (
    FeasibilityStatus,
    MultiSupplierAllocationRequest,
    SupplierAllocationInput,
)
from modules.allocation_feasibility import evaluate_allocation_feasibility
from modules.multi_supplier_allocation import (
    ALLOCATION_ENGINE_VERSION,
    AllocationStatus,
    recommend_multi_supplier_allocation,
)


def request(**overrides):
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


def supplier(name, capacity=600, eligible=True, risk=75, esg=70, tco=1.0, score=80, performance=85):
    return SupplierAllocationInput(
        supplier_id=name,
        technical_eligible=eligible,
        adjusted_tco_unit_usd=tco,
        total_score=score,
        risk_score=risk,
        performance_score=performance,
        esg_score=esg,
        supplier_capacity=capacity,
    )


def six_suppliers():
    return [
        supplier("Vendor A", 600, tco=1.00, score=95),
        supplier("Vendor B", 500, tco=1.05, score=90),
        supplier("Vendor C", 450, tco=1.10, score=85),
        supplier("Vendor D", 400, tco=1.20, score=80),
        supplier("Vendor E", 300, tco=1.30, score=75),
        supplier("Vendor F", 700, eligible=False, tco=0.90, score=70),
    ]


def feasibility(req=None, suppliers=None):
    req = req or request()
    suppliers = suppliers or six_suppliers()
    return evaluate_allocation_feasibility(req, [
        {
            "Supplier": item.supplier_id,
            "technical_eligible": item.technical_eligible,
            "adjusted_tco_unit_usd": item.adjusted_tco_unit_usd,
            "total_score": item.total_score,
            "risk_score": item.risk_score,
            "performance_score": item.performance_score,
            "esg_score": item.esg_score,
            "Supplier Capacity": item.supplier_capacity,
        }
        for item in suppliers
    ])


def allocate(req=None, suppliers=None, gate1=None):
    req = req or request()
    suppliers = suppliers or six_suppliers()
    gate1 = gate1 or feasibility(req, suppliers)
    return recommend_multi_supplier_allocation(req, suppliers, gate1)


def test_six_bidders_five_eligible_k3_recommends_allocation():
    result = allocate()
    assert result.status_code is AllocationStatus.ALLOCATION_RECOMMENDED
    assert len(result.selected_supplier_ids) == 3
    assert len(result.exclusion_reasons) == 3


@pytest.mark.parametrize(("k", "maximum", "capacities"), [(1, 100, [1000]), (2, 70, [700, 500]), (3, 60, [600, 500, 400])])
def test_k1_k2_k3_exact_awardee_counts(k, maximum, capacities):
    req = request(required_awardee_count=k, maximum_supplier_share_pct=maximum, minimum_continuity_share_pct=10)
    suppliers = [supplier(f"Vendor {index}", capacity, tco=1 + index / 10) for index, capacity in enumerate(capacities, 1)]
    result = allocate(req, suppliers)
    assert result.status_code is AllocationStatus.ALLOCATION_RECOMMENDED
    assert sum(value > 0 for value in result.allocation_pct_by_supplier.values()) == k
    assert sum(result.allocation_pct_by_supplier.values()) == pytest.approx(100)


def test_k1_role_is_sole_source():
    req = request(required_awardee_count=1, maximum_supplier_share_pct=100, minimum_continuity_share_pct=0)
    result = allocate(req, [supplier("Vendor A", 1000)])
    assert result.supplier_roles == {"vendor a": "Sole Source"}


def test_k2_roles_are_primary_and_secondary():
    req = request(required_awardee_count=2, maximum_supplier_share_pct=70, minimum_continuity_share_pct=20)
    result = allocate(req, [supplier("Vendor A", 700, tco=1.0), supplier("Vendor B", 500, tco=1.2)])
    assert set(result.supplier_roles.values()) == {"Primary", "Secondary"}


def test_k3_roles_include_continuity():
    assert set(allocate().supplier_roles.values()) == {"Primary", "Secondary", "Continuity"}


def test_minimum_and_maximum_shares_are_enforced():
    req = request(minimum_awarded_share_pct=15, maximum_supplier_share_pct=55)
    gate1 = feasibility(req)
    result = allocate(req, gate1=gate1)
    assert min(result.allocation_pct_by_supplier.values()) >= 15
    assert all(result.allocation_pct_by_supplier[sid] <= gate1.maximum_feasible_share_by_supplier[sid] for sid in result.selected_supplier_ids)


def test_required_higher_cost_supplier_remains_included():
    req = request(required_supplier_ids=("Vendor E",))
    result = allocate(req)
    assert "vendor e" in result.selected_supplier_ids
    assert result.allocation_pct_by_supplier["vendor e"] > 0


def test_excluded_supplier_receives_zero_and_reason():
    req = request(excluded_supplier_ids=("Vendor A",))
    result = allocate(req)
    assert "vendor a" not in result.allocation_pct_by_supplier
    assert "Explicitly excluded" in " ".join(result.exclusion_reasons["vendor a"])


def test_technical_risk_and_esg_ineligible_suppliers_receive_zero():
    suppliers = six_suppliers()
    suppliers[1] = replace(suppliers[1], risk_score=10)
    suppliers[2] = replace(suppliers[2], esg_score=10)
    result = allocate(request(required_awardee_count=3), suppliers)
    assert "vendor f" not in result.allocation_pct_by_supplier
    assert "Technically ineligible." in result.exclusion_reasons["vendor f"]
    assert "Below the minimum risk-score threshold." in result.exclusion_reasons["vendor b"]
    assert "Below the minimum ESG-score threshold." in result.exclusion_reasons["vendor c"]


def test_continuity_floor_for_k2():
    req = request(required_awardee_count=2, maximum_supplier_share_pct=80, minimum_continuity_share_pct=25)
    result = allocate(req, [supplier("Vendor A", 800, tco=1), supplier("Vendor B", 500, tco=2)])
    assert sum(value >= 25 for value in result.allocation_pct_by_supplier.values()) >= 1


def test_continuity_floor_for_k3():
    req = request(required_awardee_count=3, maximum_supplier_share_pct=70, minimum_continuity_share_pct=20)
    result = allocate(req, [supplier("Vendor A", 700, tco=1), supplier("Vendor B", 500, tco=2), supplier("Vendor C", 500, tco=3)])
    assert sum(value >= 20 for value in result.allocation_pct_by_supplier.values()) >= 2


def test_allocated_volume_annual_tco_and_capacity_utilization():
    req = request(required_awardee_count=2, maximum_supplier_share_pct=70, minimum_continuity_share_pct=20)
    suppliers = [supplier("Vendor A", 700, tco=2), supplier("Vendor B", 500, tco=3)]
    result = allocate(req, suppliers)
    for item in suppliers:
        sid = item.supplier_id
        share = result.allocation_pct_by_supplier[sid]
        assert result.allocated_volume_by_supplier[sid] == pytest.approx(req.annual_volume * share / 100)
        assert result.annual_tco_by_supplier[sid] == pytest.approx(result.allocated_volume_by_supplier[sid] * item.adjusted_tco_unit_usd)
        assert result.capacity_utilization_pct_by_supplier[sid] == pytest.approx(result.allocated_volume_by_supplier[sid] / item.supplier_capacity * 100)
    assert result.portfolio_annual_tco == pytest.approx(sum(result.annual_tco_by_supplier.values()))


def test_capacity_utilization_does_not_exceed_ceiling():
    req = request(required_awardee_count=2, maximum_supplier_share_pct=70, capacity_utilization_ceiling_pct=80, minimum_continuity_share_pct=20)
    result = allocate(req, [supplier("Vendor A", 900, tco=1), supplier("Vendor B", 700, tco=2)])
    assert max(result.capacity_utilization_pct_by_supplier.values()) <= 80 + 1e-7


def test_hhi_calculation():
    result = allocate()
    assert result.portfolio_metrics["hhi"] == pytest.approx(sum((value / 100) ** 2 for value in result.allocation_pct_by_supplier.values()))


def test_lowest_portfolio_annual_tco_is_selected():
    result = allocate()
    assert "vendor a" in result.selected_supplier_ids
    assert "vendor b" in result.selected_supplier_ids
    assert "vendor e" not in result.selected_supplier_ids


def test_tie_breaking_is_lexical_and_deterministic():
    req = request(required_awardee_count=2, maximum_supplier_share_pct=60, minimum_continuity_share_pct=20)
    suppliers = [supplier("Vendor C", 600), supplier("Vendor A", 600), supplier("Vendor B", 600)]
    first = allocate(req, suppliers)
    second = allocate(req, list(reversed(suppliers)))
    assert first.to_json() == second.to_json()
    assert first.selected_supplier_ids == ("vendor a", "vendor b")


def test_repeated_execution_is_deterministic():
    assert allocate().to_json() == allocate().to_json()


def test_source_contracts_are_not_mutated():
    req = request()
    suppliers = six_suppliers()
    gate1 = feasibility(req, suppliers)
    before = (req.to_json(), [repr(item) for item in suppliers], gate1.to_json())
    recommend_multi_supplier_allocation(req, suppliers, gate1)
    after = (req.to_json(), [repr(item) for item in suppliers], gate1.to_json())
    assert after == before


def test_no_exact_allocation_returns_governed_state():
    req = request(required_awardee_count=2, maximum_supplier_share_pct=70, minimum_continuity_share_pct=20)
    suppliers = [supplier("Vendor A", 700), supplier("Vendor B", 700)]
    gate1 = feasibility(req, suppliers)
    evidence = tuple({**dict(item), "capacity_supported_share_pct": 40.0, "maximum_feasible_share_pct": 40.0, "supplier_capacity": 400.0} for item in gate1.supplier_capacity_evidence)
    constrained_suppliers = [replace(item, supplier_capacity=400) for item in suppliers]
    broken = replace(gate1, supplier_capacity_evidence=evidence, maximum_feasible_share_by_supplier={"vendor a": 40, "vendor b": 40})
    result = allocate(req, constrained_suppliers, broken)
    assert result.status_code is AllocationStatus.NO_EXACT_ALLOCATION
    assert not result.feasible


def test_indeterminate_feasibility_is_blocked():
    req = request()
    gate1 = replace(feasibility(req), feasible=False, status_code=FeasibilityStatus.ENUMERATION_LIMIT_REACHED, decision_complete=False)
    result = allocate(req, six_suppliers(), gate1)
    assert result.status_code is AllocationStatus.FEASIBILITY_INDETERMINATE
    assert result.decision_complete is False


def test_infeasible_gate1_result_is_blocked():
    req = request()
    gate1 = replace(feasibility(req), feasible=False, status_code=FeasibilityStatus.INSUFFICIENT_CAPACITY)
    assert allocate(req, six_suppliers(), gate1).status_code is AllocationStatus.FEASIBILITY_NOT_CONFIRMED


def test_supplier_universe_mismatch_is_blocked():
    req = request()
    suppliers = six_suppliers()
    assert allocate(req, suppliers[:-2], feasibility(req, suppliers)).status_code is AllocationStatus.SUPPLIER_UNIVERSE_MISMATCH


def test_contract_version_mismatch_is_blocked():
    req = request()
    gate1 = replace(feasibility(req), contract_version="WRONG")
    assert allocate(req, six_suppliers(), gate1).status_code is AllocationStatus.INPUT_CONTRACT_MISMATCH


def test_missing_technical_eligibility_mapping_is_rejected_not_defaulted():
    req = request()
    result = recommend_multi_supplier_allocation(req, [{"supplier_id": "vendor a"}], feasibility(req))
    assert result.status_code is AllocationStatus.INVALID_SUPPLIER_INPUT


def test_allocation_reconciles_exactly_to_100_and_is_read_only():
    result = allocate()
    assert sum(result.allocation_pct_by_supplier.values()) == pytest.approx(100)
    with pytest.raises(TypeError):
        result.allocation_pct_by_supplier["vendor a"] = 99


def test_residual_follows_ranking_and_not_input_order():
    req = request(required_awardee_count=2, maximum_supplier_share_pct=80, minimum_continuity_share_pct=20)
    suppliers = [supplier("Expensive", 800, tco=2), supplier("Cheap", 800, tco=1)]
    result = allocate(req, list(reversed(suppliers)))
    assert result.allocation_pct_by_supplier["cheap"] > result.allocation_pct_by_supplier["expensive"]


def test_inclusion_and_exclusion_reasons_are_complete():
    result = allocate()
    assert set(result.inclusion_reasons) == set(result.selected_supplier_ids)
    assert set(result.exclusion_reasons) == {item.supplier_id for item in six_suppliers()} - set(result.selected_supplier_ids)
    assert all(result.inclusion_reasons.values())
    assert all(result.exclusion_reasons.values())


def test_result_contract_version_engine_version_and_human_review():
    result = allocate()
    assert result.contract_version == "AIPC-MULTI-ALLOC-1.0"
    assert result.allocation_engine_version == ALLOCATION_ENGINE_VERSION
    assert result.human_review_required is True
    assert "human procurement approval" in " ".join(result.warnings).lower()
    assert json.loads(result.to_json())["status_code"] == "ALLOCATION_RECOMMENDED"


def test_result_contract_is_immutable():
    result = allocate()
    with pytest.raises(TypeError):
        result.portfolio_metrics["hhi"] = 0
    with pytest.raises(TypeError):
        result.inclusion_reasons[result.selected_supplier_ids[0]] = ("changed",)


@pytest.mark.parametrize(("category", "commodity"), [
    ("Packaging Procurement", "Corrugated Board"),
    ("Packaging Procurement", "PET"),
    ("Packaging Procurement", "Kraft Paper"),
    ("Packaging Procurement", "Flexible Laminates"),
    ("Raw Material Procurement", "Steel"),
    ("Generic Uploaded RFQ", "Client Material"),
])
def test_common_engine_is_cross_category(category, commodity):
    assert allocate(request(category=category, commodity=commodity)).status_code is AllocationStatus.ALLOCATION_RECOMMENDED


def test_duplicate_supplier_inputs_are_rejected():
    req = request()
    suppliers = six_suppliers()
    assert allocate(req, suppliers + [suppliers[0]], feasibility(req, suppliers)).status_code is AllocationStatus.INVALID_SUPPLIER_INPUT


def test_non_contract_supplier_input_is_rejected():
    req = request()
    assert recommend_multi_supplier_allocation(req, [object()], feasibility(req)).status_code is AllocationStatus.INVALID_SUPPLIER_INPUT


def test_primary_role_is_highest_share_with_rank_tie_break():
    result = allocate()
    primary = next(sid for sid, role in result.supplier_roles.items() if role == "Primary")
    assert result.allocation_pct_by_supplier[primary] == max(result.allocation_pct_by_supplier.values())


def test_exactly_k_selected_ids_match_positive_allocations():
    result = allocate()
    assert set(result.selected_supplier_ids) == {sid for sid, share in result.allocation_pct_by_supplier.items() if share > 0}


def test_selected_required_supplier_has_inclusion_evidence():
    result = allocate(request(required_supplier_ids=("Vendor E",)))
    assert "vendor e" in result.inclusion_reasons
    assert "Recommended allocation" in " ".join(result.inclusion_reasons["vendor e"])


@pytest.mark.parametrize("new_capacity", [500, 700])
def test_changed_capacity_lower_or_higher_than_gate1_is_blocked(new_capacity):
    req = request()
    suppliers = six_suppliers()
    gate1 = feasibility(req, suppliers)
    changed = [replace(item, supplier_capacity=new_capacity) if item.supplier_id == "vendor a" else item for item in suppliers]
    result = allocate(req, changed, gate1)
    assert result.status_code is AllocationStatus.FEASIBILITY_EVIDENCE_MISMATCH
    assert "vendor a" in " ".join(result.warnings)


def test_zero_gate2_capacity_is_governed_not_zero_division():
    req = request()
    suppliers = six_suppliers()
    gate1 = feasibility(req, suppliers)
    changed = [replace(item, supplier_capacity=0) if item.supplier_id == "vendor a" else item for item in suppliers]
    result = allocate(req, changed, gate1)
    assert result.status_code is AllocationStatus.FEASIBILITY_EVIDENCE_MISMATCH


def test_capacity_supported_share_mismatch_is_blocked():
    req = request()
    suppliers = six_suppliers()
    gate1 = feasibility(req, suppliers)
    evidence = tuple({**dict(item), "capacity_supported_share_pct": float(item["capacity_supported_share_pct"]) + 1} if item["supplier_id"] == "vendor a" else dict(item) for item in gate1.supplier_capacity_evidence)
    result = allocate(req, suppliers, replace(gate1, supplier_capacity_evidence=evidence))
    assert result.status_code is AllocationStatus.FEASIBILITY_EVIDENCE_MISMATCH


def test_maximum_feasible_share_mismatch_is_blocked():
    req = request()
    suppliers = six_suppliers()
    gate1 = feasibility(req, suppliers)
    maxima = dict(gate1.maximum_feasible_share_by_supplier)
    maxima["vendor a"] -= 1
    result = allocate(req, suppliers, replace(gate1, maximum_feasible_share_by_supplier=maxima))
    assert result.status_code is AllocationStatus.FEASIBILITY_EVIDENCE_MISMATCH


def test_capacity_evidence_comparison_is_row_order_independent():
    req = request()
    suppliers = six_suppliers()
    gate1 = feasibility(req, suppliers)
    assert allocate(req, suppliers, gate1).to_json() == allocate(req, list(reversed(suppliers)), gate1).to_json()


def test_post_floor_remaining_headroom_breaks_otherwise_equal_rank():
    req = request(required_awardee_count=2, minimum_awarded_share_pct=10, minimum_continuity_share_pct=30, maximum_supplier_share_pct=80)
    suppliers = [supplier("Vendor A", 750, tco=1, score=80), supplier("Vendor B", 800, tco=1, score=80)]
    result = allocate(req, suppliers)
    assert result.status_code is AllocationStatus.ALLOCATION_RECOMMENDED
    assert result.allocation_pct_by_supplier["vendor b"] > result.allocation_pct_by_supplier["vendor a"]


def test_lower_ranked_supplier_gets_no_residual_while_higher_ranked_has_headroom():
    req = request(required_awardee_count=2, minimum_awarded_share_pct=10, minimum_continuity_share_pct=20, maximum_supplier_share_pct=80)
    suppliers = [supplier("Cheap", 800, tco=1), supplier("Expensive", 800, tco=2)]
    result = allocate(req, suppliers)
    assert result.allocation_pct_by_supplier["cheap"] == pytest.approx(80)
    assert result.allocation_pct_by_supplier["expensive"] == pytest.approx(20)


def test_final_rounded_allocation_satisfies_all_invariants():
    req = request(required_awardee_count=3, minimum_awarded_share_pct=10.12345678, minimum_continuity_share_pct=15.12345678, maximum_supplier_share_pct=60)
    suppliers = six_suppliers()
    result = allocate(req, suppliers)
    assert result.status_code is AllocationStatus.ALLOCATION_RECOMMENDED
    assert sum(result.allocation_pct_by_supplier.values()) == pytest.approx(100, abs=1e-7)
    assert min(result.allocation_pct_by_supplier.values()) >= req.minimum_awarded_share_pct - 1e-7
    gate1 = feasibility(req, suppliers)
    assert all(result.allocation_pct_by_supplier[sid] <= gate1.maximum_feasible_share_by_supplier[sid] + 1e-7 for sid in result.selected_supplier_ids)
    assert sum(value >= req.minimum_continuity_share_pct - 1e-7 for value in result.allocation_pct_by_supplier.values()) >= req.required_awardee_count - 1
    assert max(result.capacity_utilization_pct_by_supplier.values()) <= req.capacity_utilization_ceiling_pct + 1e-7


def test_success_and_failure_serialization_remain_deterministic():
    success = allocate()
    req = request()
    suppliers = six_suppliers()
    gate1 = feasibility(req, suppliers)
    changed = [replace(item, supplier_capacity=500) if item.supplier_id == "vendor a" else item for item in suppliers]
    failure = allocate(req, changed, gate1)
    assert success.to_json() == allocate().to_json()
    assert failure.to_json() == allocate(req, list(reversed(changed)), gate1).to_json()
    assert json.loads(failure.to_json())["status_code"] == "FEASIBILITY_EVIDENCE_MISMATCH"
