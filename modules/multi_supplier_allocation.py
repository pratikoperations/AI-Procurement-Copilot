"""Isolated deterministic exactly-K multi-supplier allocation engine.

This module is not integrated into production application routes. It consumes the
accepted Gate 1 contracts and produces a governed recommendation for human review.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
import math
from types import MappingProxyType
from typing import Any, Iterable, Mapping, Sequence

from modules.allocation_contract import (
    ALLOCATION_CONTRACT_VERSION,
    FeasibilityStatus,
    MultiSupplierAllocationRequest,
    MultiSupplierFeasibilityResult,
    SupplierAllocationInput,
)

ALLOCATION_ENGINE_VERSION = "AIPC-MULTI-ALLOC-ENGINE-1.0"
ALLOCATION_INCREMENT_PCT = 1.0
NUMERIC_TOLERANCE = 1e-7


class AllocationStatus(str, Enum):
    ALLOCATION_RECOMMENDED = "ALLOCATION_RECOMMENDED"
    INPUT_CONTRACT_MISMATCH = "INPUT_CONTRACT_MISMATCH"
    FEASIBILITY_NOT_CONFIRMED = "FEASIBILITY_NOT_CONFIRMED"
    FEASIBILITY_INDETERMINATE = "FEASIBILITY_INDETERMINATE"
    NO_EXACT_ALLOCATION = "NO_EXACT_ALLOCATION"
    SUPPLIER_UNIVERSE_MISMATCH = "SUPPLIER_UNIVERSE_MISMATCH"
    INVALID_SUPPLIER_INPUT = "INVALID_SUPPLIER_INPUT"
    NUMERIC_RECONCILIATION_FAILURE = "NUMERIC_RECONCILIATION_FAILURE"


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in sorted(value.items(), key=lambda p: str(p[0]))})
    if isinstance(value, (list, tuple, set, frozenset)):
        return tuple(_freeze(item) for item in value)
    return value


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _thaw(item) for key, item in sorted(value.items(), key=lambda p: str(p[0]))}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    if isinstance(value, Enum):
        return value.value
    return value


@dataclass(frozen=True, slots=True)
class MultiSupplierAllocationResult:
    contract_version: str
    allocation_engine_version: str
    feasible: bool
    decision_complete: bool
    status_code: AllocationStatus
    summary: str
    selected_supplier_ids: tuple[str, ...]
    allocation_pct_by_supplier: Mapping[str, float]
    allocated_volume_by_supplier: Mapping[str, float]
    unit_tco_by_supplier: Mapping[str, float]
    annual_tco_by_supplier: Mapping[str, float]
    portfolio_annual_tco: float
    capacity_utilization_pct_by_supplier: Mapping[str, float]
    supplier_roles: Mapping[str, str]
    inclusion_reasons: Mapping[str, tuple[str, ...]]
    exclusion_reasons: Mapping[str, tuple[str, ...]]
    binding_constraints: tuple[str, ...]
    portfolio_metrics: Mapping[str, float]
    source_feasibility_status: str
    warnings: tuple[str, ...]
    human_review_required: bool = True

    def __post_init__(self) -> None:
        for name in (
            "allocation_pct_by_supplier", "allocated_volume_by_supplier", "unit_tco_by_supplier",
            "annual_tco_by_supplier", "capacity_utilization_pct_by_supplier", "supplier_roles",
            "inclusion_reasons", "exclusion_reasons", "portfolio_metrics",
        ):
            object.__setattr__(self, name, _freeze(getattr(self, name)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract_version": self.contract_version,
            "allocation_engine_version": self.allocation_engine_version,
            "feasible": self.feasible,
            "decision_complete": self.decision_complete,
            "status_code": self.status_code.value,
            "summary": self.summary,
            "selected_supplier_ids": list(self.selected_supplier_ids),
            "allocation_pct_by_supplier": _thaw(self.allocation_pct_by_supplier),
            "allocated_volume_by_supplier": _thaw(self.allocated_volume_by_supplier),
            "unit_tco_by_supplier": _thaw(self.unit_tco_by_supplier),
            "annual_tco_by_supplier": _thaw(self.annual_tco_by_supplier),
            "portfolio_annual_tco": self.portfolio_annual_tco,
            "capacity_utilization_pct_by_supplier": _thaw(self.capacity_utilization_pct_by_supplier),
            "supplier_roles": _thaw(self.supplier_roles),
            "inclusion_reasons": _thaw(self.inclusion_reasons),
            "exclusion_reasons": _thaw(self.exclusion_reasons),
            "binding_constraints": list(self.binding_constraints),
            "portfolio_metrics": _thaw(self.portfolio_metrics),
            "source_feasibility_status": self.source_feasibility_status,
            "warnings": list(self.warnings),
            "human_review_required": self.human_review_required,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"), allow_nan=False)


def _empty_result(
    status: AllocationStatus,
    summary: str,
    feasibility: MultiSupplierFeasibilityResult,
    *,
    warnings: Iterable[str] = (),
    decision_complete: bool = True,
) -> MultiSupplierAllocationResult:
    return MultiSupplierAllocationResult(
        contract_version=ALLOCATION_CONTRACT_VERSION,
        allocation_engine_version=ALLOCATION_ENGINE_VERSION,
        feasible=False,
        decision_complete=decision_complete,
        status_code=status,
        summary=summary,
        selected_supplier_ids=(),
        allocation_pct_by_supplier={},
        allocated_volume_by_supplier={},
        unit_tco_by_supplier={},
        annual_tco_by_supplier={},
        portfolio_annual_tco=0.0,
        capacity_utilization_pct_by_supplier={},
        supplier_roles={},
        inclusion_reasons={},
        exclusion_reasons={},
        binding_constraints=(),
        portfolio_metrics={},
        source_feasibility_status=feasibility.status_code.value,
        warnings=tuple(sorted(set(warnings))),
        human_review_required=True,
    )


def _ranking_key(supplier: SupplierAllocationInput, maximum_share: float) -> tuple[Any, ...]:
    return (
        supplier.adjusted_tco_unit_usd,
        -supplier.total_score,
        -supplier.risk_score,
        -supplier.performance_score,
        -supplier.esg_score,
        -maximum_share,
        supplier.supplier_id,
    )


def _allocate_portfolio(
    request: MultiSupplierAllocationRequest,
    portfolio: tuple[str, ...],
    suppliers: Mapping[str, SupplierAllocationInput],
    maximum_shares: Mapping[str, float],
) -> Mapping[str, float] | None:
    minimum = request.minimum_awarded_share_pct
    continuity = max(minimum, request.minimum_continuity_share_pct)
    allocations = {supplier_id: minimum for supplier_id in portfolio}
    ranking = sorted(portfolio, key=lambda sid: _ranking_key(suppliers[sid], maximum_shares[sid]))

    # The strongest-ranked supplier remains the primary candidate. Every other
    # supplier receives the continuity floor before residual allocation.
    if len(portfolio) > 1:
        for supplier_id in ranking[1:]:
            allocations[supplier_id] = continuity

    if any(allocations[sid] > maximum_shares[sid] + NUMERIC_TOLERANCE for sid in portfolio):
        return None

    remaining = 100.0 - sum(allocations.values())
    if remaining < -NUMERIC_TOLERANCE:
        return None

    # Fill residual only through governed ranking and available headroom.
    while remaining > NUMERIC_TOLERANCE:
        progressed = False
        for supplier_id in ranking:
            headroom = maximum_shares[supplier_id] - allocations[supplier_id]
            if headroom <= NUMERIC_TOLERANCE:
                continue
            increment = min(ALLOCATION_INCREMENT_PCT, remaining, headroom)
            allocations[supplier_id] += increment
            remaining -= increment
            progressed = True
            if remaining <= NUMERIC_TOLERANCE:
                break
        if not progressed:
            return None

    allocations = {sid: round(value, 8) for sid, value in allocations.items()}
    residual = round(100.0 - sum(allocations.values()), 8)
    if abs(residual) > NUMERIC_TOLERANCE:
        for supplier_id in ranking:
            candidate = allocations[supplier_id] + residual
            if minimum - NUMERIC_TOLERANCE <= candidate <= maximum_shares[supplier_id] + NUMERIC_TOLERANCE:
                allocations[supplier_id] = round(candidate, 8)
                residual = round(100.0 - sum(allocations.values()), 8)
                break
    if abs(residual) > NUMERIC_TOLERANCE:
        return None
    if sum(value > NUMERIC_TOLERANCE for value in allocations.values()) != request.required_awardee_count:
        return None
    if len(portfolio) > 1 and sum(value + NUMERIC_TOLERANCE >= continuity for value in allocations.values()) < len(portfolio) - 1:
        return None
    return MappingProxyType(dict(sorted(allocations.items())))


def _roles(
    portfolio: tuple[str, ...],
    allocations: Mapping[str, float],
    suppliers: Mapping[str, SupplierAllocationInput],
    maximum_shares: Mapping[str, float],
) -> dict[str, str]:
    if len(portfolio) == 1:
        return {portfolio[0]: "Sole Source"}
    ranked = sorted(
        portfolio,
        key=lambda sid: (-allocations[sid], _ranking_key(suppliers[sid], maximum_shares[sid])),
    )
    roles = {ranked[0]: "Primary", ranked[1]: "Secondary"}
    roles.update({supplier_id: "Continuity" for supplier_id in ranked[2:]})
    return dict(sorted(roles.items()))


def _exclusion_reasons(
    request: MultiSupplierAllocationRequest,
    suppliers: Sequence[SupplierAllocationInput],
    selected: set[str],
    maximum_shares: Mapping[str, float],
) -> dict[str, tuple[str, ...]]:
    reasons: dict[str, tuple[str, ...]] = {}
    for supplier in sorted(suppliers, key=lambda item: item.supplier_id):
        if supplier.supplier_id in selected:
            continue
        items: list[str] = []
        if supplier.supplier_id in request.excluded_supplier_ids:
            items.append("Explicitly excluded by the allocation request.")
        if not supplier.technical_eligible:
            items.append("Technically ineligible.")
        if supplier.risk_score < request.minimum_risk_score:
            items.append("Below the minimum risk-score threshold.")
        if supplier.esg_score < request.minimum_esg_score:
            items.append("Below the minimum ESG-score threshold.")
        if maximum_shares.get(supplier.supplier_id, 0.0) + NUMERIC_TOLERANCE < request.minimum_awarded_share_pct:
            items.append("Insufficient capacity for the minimum awarded share.")
        if not items:
            items.extend((
                "Not selected in the lowest governed portfolio.",
                "Required awardee count reached; displaced by a lower-TCO or stronger governed portfolio.",
            ))
        reasons[supplier.supplier_id] = tuple(items)
    return reasons


def recommend_multi_supplier_allocation(
    request: MultiSupplierAllocationRequest,
    supplier_inputs: Sequence[SupplierAllocationInput],
    feasibility: MultiSupplierFeasibilityResult,
) -> MultiSupplierAllocationResult:
    """Recommend deterministic shares across exactly K suppliers."""
    if not isinstance(request, MultiSupplierAllocationRequest) or not isinstance(feasibility, MultiSupplierFeasibilityResult):
        raise TypeError("request and feasibility must use the accepted Gate 1 contracts")
    if request.contract_version != ALLOCATION_CONTRACT_VERSION or feasibility.contract_version != request.contract_version:
        return _empty_result(AllocationStatus.INPUT_CONTRACT_MISMATCH, "Allocation contract versions do not match.", feasibility)
    if not feasibility.decision_complete:
        return _empty_result(
            AllocationStatus.FEASIBILITY_INDETERMINATE,
            "Gate 1 feasibility is incomplete; allocation is blocked.",
            feasibility,
            warnings=("Do not treat an indeterminate feasibility result as an allocation recommendation.",),
            decision_complete=False,
        )
    if not feasibility.feasible or feasibility.status_code is not FeasibilityStatus.FEASIBLE:
        return _empty_result(AllocationStatus.FEASIBILITY_NOT_CONFIRMED, "Gate 1 feasibility was not confirmed.", feasibility)
    if not isinstance(supplier_inputs, Sequence) or isinstance(supplier_inputs, (str, bytes)):
        return _empty_result(AllocationStatus.INVALID_SUPPLIER_INPUT, "Supplier inputs must be a sequence of normalized contracts.", feasibility)
    if not supplier_inputs or any(not isinstance(item, SupplierAllocationInput) for item in supplier_inputs):
        return _empty_result(AllocationStatus.INVALID_SUPPLIER_INPUT, "Every supplier input must be a normalized SupplierAllocationInput.", feasibility)

    suppliers = sorted(supplier_inputs, key=lambda item: item.supplier_id)
    identifiers = [item.supplier_id for item in suppliers]
    if len(set(identifiers)) != len(identifiers):
        return _empty_result(AllocationStatus.INVALID_SUPPLIER_INPUT, "Duplicate supplier identifiers are not permitted.", feasibility)
    by_id = {item.supplier_id: item for item in suppliers}
    eligible_ids = {
        item.supplier_id for item in suppliers
        if item.technical_eligible
        and item.risk_score >= request.minimum_risk_score
        and item.esg_score >= request.minimum_esg_score
        and item.supplier_id not in request.excluded_supplier_ids
    }
    evidence_ids = {str(item["supplier_id"]) for item in feasibility.supplier_capacity_evidence}
    if eligible_ids != evidence_ids:
        return _empty_result(AllocationStatus.SUPPLIER_UNIVERSE_MISMATCH, "Supplier universe differs from Gate 1 feasibility evidence.", feasibility)

    maximum_shares = dict(feasibility.maximum_feasible_share_by_supplier)
    candidates: list[dict[str, Any]] = []
    for raw_portfolio in feasibility.feasible_supplier_combinations:
        portfolio = tuple(sorted(raw_portfolio))
        if len(portfolio) != request.required_awardee_count or any(sid not in by_id for sid in portfolio):
            continue
        allocations = _allocate_portfolio(request, portfolio, by_id, maximum_shares)
        if allocations is None:
            continue
        allocated_volume = {sid: request.annual_volume * allocations[sid] / 100.0 for sid in portfolio}
        annual_tco = {sid: allocated_volume[sid] * by_id[sid].adjusted_tco_unit_usd for sid in portfolio}
        capacity_utilization = {
            sid: allocated_volume[sid] / float(by_id[sid].supplier_capacity) * 100.0
            for sid in portfolio
        }
        if any(value > request.capacity_utilization_ceiling_pct + NUMERIC_TOLERANCE for value in capacity_utilization.values()):
            continue
        portfolio_tco = sum(annual_tco.values())
        hhi = sum((allocations[sid] / 100.0) ** 2 for sid in portfolio)
        weighted_performance = sum(allocations[sid] / 100.0 * by_id[sid].performance_score for sid in portfolio)
        weighted_esg = sum(allocations[sid] / 100.0 * by_id[sid].esg_score for sid in portfolio)
        aggregate_headroom = sum(maximum_shares[sid] - allocations[sid] for sid in portfolio)
        objective = (
            round(portfolio_tco, 8), round(hhi, 10),
            -min(by_id[sid].risk_score for sid in portfolio),
            -round(weighted_performance, 8), -round(weighted_esg, 8),
            -round(aggregate_headroom, 8), portfolio,
        )
        candidates.append({
            "portfolio": portfolio, "allocations": allocations, "allocated_volume": allocated_volume,
            "annual_tco": annual_tco, "capacity_utilization": capacity_utilization,
            "portfolio_tco": portfolio_tco, "hhi": hhi,
            "weighted_performance": weighted_performance, "weighted_esg": weighted_esg,
            "aggregate_headroom": aggregate_headroom, "objective": objective,
        })

    if not candidates:
        return _empty_result(AllocationStatus.NO_EXACT_ALLOCATION, "No exact 100% allocation satisfies all Gate 2 constraints.", feasibility)
    chosen = min(candidates, key=lambda item: item["objective"])
    portfolio = chosen["portfolio"]
    allocations = chosen["allocations"]
    if abs(sum(allocations.values()) - 100.0) > NUMERIC_TOLERANCE:
        return _empty_result(AllocationStatus.NUMERIC_RECONCILIATION_FAILURE, "Allocation percentages did not reconcile to 100%.", feasibility)

    roles = _roles(portfolio, allocations, by_id, maximum_shares)
    ranking = sorted(portfolio, key=lambda sid: _ranking_key(by_id[sid], maximum_shares[sid]))
    inclusion = {
        sid: (
            "Technical and commercial eligibility confirmed.",
            f"Selected in the lowest governed feasible portfolio; governed rank {ranking.index(sid) + 1} of {len(portfolio)}.",
            f"Recommended allocation {allocations[sid]:.2f}% with role {roles[sid]}.",
            f"Unit TCO {by_id[sid].adjusted_tco_unit_usd:.6f} USD and total score {by_id[sid].total_score:.2f}.",
            f"Maximum feasible share {maximum_shares[sid]:.2f}%; capacity utilization {chosen['capacity_utilization'][sid]:.2f}%.",
        )
        for sid in portfolio
    }
    exclusion = _exclusion_reasons(request, suppliers, set(portfolio), maximum_shares)
    return MultiSupplierAllocationResult(
        contract_version=request.contract_version,
        allocation_engine_version=ALLOCATION_ENGINE_VERSION,
        feasible=True,
        decision_complete=True,
        status_code=AllocationStatus.ALLOCATION_RECOMMENDED,
        summary=f"Recommended exactly-{request.required_awardee_count} supplier allocation totals 100%.",
        selected_supplier_ids=portfolio,
        allocation_pct_by_supplier=dict(allocations),
        allocated_volume_by_supplier={sid: round(chosen["allocated_volume"][sid], 8) for sid in portfolio},
        unit_tco_by_supplier={sid: by_id[sid].adjusted_tco_unit_usd for sid in portfolio},
        annual_tco_by_supplier={sid: round(chosen["annual_tco"][sid], 8) for sid in portfolio},
        portfolio_annual_tco=round(chosen["portfolio_tco"], 8),
        capacity_utilization_pct_by_supplier={sid: round(chosen["capacity_utilization"][sid], 8) for sid in portfolio},
        supplier_roles=roles,
        inclusion_reasons=inclusion,
        exclusion_reasons=exclusion,
        binding_constraints=("exact awardee count", "100% reconciliation", "capacity ceiling", "continuity share", "minimum and maximum share"),
        portfolio_metrics={
            "hhi": round(chosen["hhi"], 10),
            "weighted_performance_score": round(chosen["weighted_performance"], 8),
            "weighted_esg_score": round(chosen["weighted_esg"], 8),
            "aggregate_capacity_headroom_pct": round(chosen["aggregate_headroom"], 8),
        },
        source_feasibility_status=feasibility.status_code.value,
        warnings=(
            "Allocation is decision support only; human procurement approval remains mandatory.",
            "Supplier capacity is supplied evidence and has not been independently verified.",
        ),
        human_review_required=True,
    )
