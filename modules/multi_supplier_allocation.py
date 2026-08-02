"""Isolated deterministic exactly-K multi-supplier allocation engine."""
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
EVIDENCE_TOLERANCE = 1e-7


class AllocationStatus(str, Enum):
    ALLOCATION_RECOMMENDED = "ALLOCATION_RECOMMENDED"
    INPUT_CONTRACT_MISMATCH = "INPUT_CONTRACT_MISMATCH"
    FEASIBILITY_NOT_CONFIRMED = "FEASIBILITY_NOT_CONFIRMED"
    FEASIBILITY_INDETERMINATE = "FEASIBILITY_INDETERMINATE"
    NO_EXACT_ALLOCATION = "NO_EXACT_ALLOCATION"
    SUPPLIER_UNIVERSE_MISMATCH = "SUPPLIER_UNIVERSE_MISMATCH"
    FEASIBILITY_EVIDENCE_MISMATCH = "FEASIBILITY_EVIDENCE_MISMATCH"
    INVALID_SUPPLIER_INPUT = "INVALID_SUPPLIER_INPUT"
    NUMERIC_RECONCILIATION_FAILURE = "NUMERIC_RECONCILIATION_FAILURE"


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {str(key): _freeze(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))}
        )
    if isinstance(value, (list, tuple, set, frozenset)):
        return tuple(_freeze(item) for item in value)
    return value


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _thaw(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))}
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
            "allocation_pct_by_supplier",
            "allocated_volume_by_supplier",
            "unit_tco_by_supplier",
            "annual_tco_by_supplier",
            "capacity_utilization_pct_by_supplier",
            "supplier_roles",
            "inclusion_reasons",
            "exclusion_reasons",
            "portfolio_metrics",
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


def _base_ranking_key(supplier: SupplierAllocationInput) -> tuple[Any, ...]:
    return (
        supplier.adjusted_tco_unit_usd,
        -supplier.total_score,
        -supplier.risk_score,
        -supplier.performance_score,
        -supplier.esg_score,
    )


def _remaining_headroom_key(
    supplier: SupplierAllocationInput,
    maximum_share: float,
    current_allocation: float,
) -> tuple[Any, ...]:
    remaining_headroom = maximum_share - current_allocation
    return (*_base_ranking_key(supplier), -remaining_headroom, supplier.supplier_id)


def _evidence_mismatches(
    request: MultiSupplierAllocationRequest,
    suppliers: Mapping[str, SupplierAllocationInput],
    feasibility: MultiSupplierFeasibilityResult,
    eligible_ids: set[str],
) -> tuple[str, ...]:
    evidence_by_id: dict[str, Mapping[str, Any]] = {}
    for evidence in feasibility.supplier_capacity_evidence:
        supplier_id = str(evidence.get("supplier_id", ""))
        if supplier_id:
            evidence_by_id[supplier_id] = evidence

    mismatches: list[str] = []
    evidence_ids = set(evidence_by_id)
    if eligible_ids != evidence_ids:
        missing = sorted(eligible_ids - evidence_ids)
        extra = sorted(evidence_ids - eligible_ids)
        if missing:
            mismatches.append("Missing Gate 1 capacity evidence: " + ", ".join(missing))
        if extra:
            mismatches.append("Unexpected Gate 1 capacity evidence: " + ", ".join(extra))
        return tuple(sorted(mismatches))

    maximum_shares = dict(feasibility.maximum_feasible_share_by_supplier)
    if set(maximum_shares) != eligible_ids:
        mismatches.append("Gate 1 maximum-feasible-share supplier set differs from the eligible supplier set")

    for supplier_id in sorted(eligible_ids):
        supplier = suppliers[supplier_id]
        evidence = evidence_by_id[supplier_id]
        capacity = supplier.supplier_capacity
        if capacity is None or not isinstance(capacity, (int, float)) or isinstance(capacity, bool):
            mismatches.append(f"{supplier_id}: Gate 2 supplier capacity is missing or non-numeric")
            continue
        capacity_value = float(capacity)
        if not math.isfinite(capacity_value) or capacity_value <= 0:
            mismatches.append(f"{supplier_id}: Gate 2 supplier capacity must be finite and greater than zero")
            continue

        try:
            evidence_capacity = float(evidence["supplier_capacity"])
            evidence_ceiling = float(evidence["capacity_utilization_ceiling_pct"])
            evidence_supported = float(evidence["capacity_supported_share_pct"])
            evidence_maximum = float(evidence["maximum_feasible_share_pct"])
            stored_maximum = float(maximum_shares[supplier_id])
        except (KeyError, TypeError, ValueError):
            mismatches.append(f"{supplier_id}: Gate 1 capacity evidence is incomplete or non-numeric")
            continue

        recomputed_supported = (
            capacity_value
            * request.capacity_utilization_ceiling_pct
            / 100.0
            / request.annual_volume
            * 100.0
        )
        recomputed_maximum = min(request.maximum_supplier_share_pct, recomputed_supported)
        comparisons = (
            (capacity_value, evidence_capacity, "supplier capacity"),
            (request.capacity_utilization_ceiling_pct, evidence_ceiling, "capacity-utilization ceiling"),
            (recomputed_supported, evidence_supported, "capacity-supported share"),
            (recomputed_maximum, evidence_maximum, "evidence maximum feasible share"),
            (recomputed_maximum, stored_maximum, "stored maximum feasible share"),
        )
        for current, recorded, label in comparisons:
            if not math.isclose(current, recorded, rel_tol=EVIDENCE_TOLERANCE, abs_tol=EVIDENCE_TOLERANCE):
                mismatches.append(
                    f"{supplier_id}: {label} mismatch (Gate 2 {current:.10g}; Gate 1 {recorded:.10g})"
                )
    return tuple(sorted(mismatches))


def _allocate_portfolio(
    request: MultiSupplierAllocationRequest,
    portfolio: tuple[str, ...],
    suppliers: Mapping[str, SupplierAllocationInput],
    maximum_shares: Mapping[str, float],
) -> Mapping[str, float] | None:
    minimum = request.minimum_awarded_share_pct
    continuity = max(minimum, request.minimum_continuity_share_pct)
    allocations = {supplier_id: minimum for supplier_id in portfolio}

    provisional_ranking = sorted(
        portfolio,
        key=lambda supplier_id: _remaining_headroom_key(
            suppliers[supplier_id], maximum_shares[supplier_id], allocations[supplier_id]
        ),
    )
    if len(portfolio) > 1:
        for supplier_id in provisional_ranking[1:]:
            allocations[supplier_id] = continuity

    if any(allocations[sid] > maximum_shares[sid] + NUMERIC_TOLERANCE for sid in portfolio):
        return None
    remaining = 100.0 - sum(allocations.values())
    if remaining < -NUMERIC_TOLERANCE:
        return None

    residual_ranking = sorted(
        portfolio,
        key=lambda supplier_id: _remaining_headroom_key(
            suppliers[supplier_id], maximum_shares[supplier_id], allocations[supplier_id]
        ),
    )
    for supplier_id in residual_ranking:
        while remaining > NUMERIC_TOLERANCE:
            headroom = maximum_shares[supplier_id] - allocations[supplier_id]
            if headroom <= NUMERIC_TOLERANCE:
                break
            increment = min(ALLOCATION_INCREMENT_PCT, remaining, headroom)
            allocations[supplier_id] += increment
            remaining -= increment
        if remaining <= NUMERIC_TOLERANCE:
            break
    if remaining > NUMERIC_TOLERANCE:
        return None

    allocations = {sid: round(value, 8) for sid, value in allocations.items()}
    residual = round(100.0 - sum(allocations.values()), 8)
    if abs(residual) > NUMERIC_TOLERANCE:
        for supplier_id in residual_ranking:
            candidate = allocations[supplier_id] + residual
            if minimum - NUMERIC_TOLERANCE <= candidate <= maximum_shares[supplier_id] + NUMERIC_TOLERANCE:
                allocations[supplier_id] = round(candidate, 8)
                residual = round(100.0 - sum(allocations.values()), 8)
                break
    if abs(residual) > NUMERIC_TOLERANCE:
        return None

    positive_count = sum(value > NUMERIC_TOLERANCE for value in allocations.values())
    continuity_count = sum(value + NUMERIC_TOLERANCE >= continuity for value in allocations.values())
    if positive_count != request.required_awardee_count:
        return None
    if any(value + NUMERIC_TOLERANCE < minimum for value in allocations.values()):
        return None
    if any(allocations[sid] > maximum_shares[sid] + NUMERIC_TOLERANCE for sid in portfolio):
        return None
    if len(portfolio) > 1 and continuity_count < len(portfolio) - 1:
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
        key=lambda sid: (
            -allocations[sid],
            _remaining_headroom_key(suppliers[sid], maximum_shares[sid], allocations[sid]),
        ),
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
        supplier_id = supplier.supplier_id
        if supplier_id in selected:
            continue
        items: list[str] = []
        if supplier_id in request.excluded_supplier_ids:
            items.append("Explicitly excluded by the allocation request.")
        if not supplier.technical_eligible:
            items.append("Technically ineligible.")
        if supplier.risk_score < request.minimum_risk_score:
            items.append("Below the minimum risk-score threshold.")
        if supplier.esg_score < request.minimum_esg_score:
            items.append("Below the minimum ESG-score threshold.")
        if maximum_shares.get(supplier_id, 0.0) + NUMERIC_TOLERANCE < request.minimum_awarded_share_pct:
            items.append("Insufficient capacity for the minimum awarded share.")
        if not items:
            items.extend(
                (
                    "Not selected in the lowest governed portfolio.",
                    "Required awardee count reached; displaced by a lower-TCO or stronger governed portfolio.",
                )
            )
        reasons[supplier_id] = tuple(items)
    return reasons


def _final_invariants_hold(
    request: MultiSupplierAllocationRequest,
    portfolio: tuple[str, ...],
    allocations: Mapping[str, float],
    maximum_shares: Mapping[str, float],
    suppliers: Mapping[str, SupplierAllocationInput],
    volumes: Mapping[str, float],
    utilization: Mapping[str, float],
) -> bool:
    minimum = request.minimum_awarded_share_pct
    continuity = max(minimum, request.minimum_continuity_share_pct)
    if len(portfolio) != request.required_awardee_count:
        return False
    if sum(value > NUMERIC_TOLERANCE for value in allocations.values()) != request.required_awardee_count:
        return False
    if abs(sum(allocations.values()) - 100.0) > NUMERIC_TOLERANCE:
        return False
    if any(value + NUMERIC_TOLERANCE < minimum for value in allocations.values()):
        return False
    if any(allocations[sid] > maximum_shares[sid] + NUMERIC_TOLERANCE for sid in portfolio):
        return False
    if len(portfolio) > 1 and sum(value + NUMERIC_TOLERANCE >= continuity for value in allocations.values()) < len(portfolio) - 1:
        return False
    if not set(request.required_supplier_ids).issubset(portfolio):
        return False
    if set(request.excluded_supplier_ids) & set(portfolio):
        return False
    if any(not suppliers[sid].technical_eligible for sid in portfolio):
        return False
    if abs(sum(volumes.values()) - request.annual_volume) > max(NUMERIC_TOLERANCE, request.annual_volume * NUMERIC_TOLERANCE):
        return False
    if any(value > request.capacity_utilization_ceiling_pct + NUMERIC_TOLERANCE for value in utilization.values()):
        return False
    return True


def recommend_multi_supplier_allocation(
    request: MultiSupplierAllocationRequest,
    supplier_inputs: Sequence[SupplierAllocationInput],
    feasibility: MultiSupplierFeasibilityResult,
) -> MultiSupplierAllocationResult:
    if not isinstance(request, MultiSupplierAllocationRequest) or not isinstance(
        feasibility, MultiSupplierFeasibilityResult
    ):
        raise TypeError("request and feasibility must use the accepted Gate 1 contracts")
    if request.contract_version != ALLOCATION_CONTRACT_VERSION or feasibility.contract_version != request.contract_version:
        return _empty_result(
            AllocationStatus.INPUT_CONTRACT_MISMATCH,
            "Allocation contract versions do not match.",
            feasibility,
        )
    if not feasibility.decision_complete:
        return _empty_result(
            AllocationStatus.FEASIBILITY_INDETERMINATE,
            "Gate 1 feasibility is incomplete; allocation is blocked.",
            feasibility,
            warnings=("Do not treat an indeterminate feasibility result as an allocation recommendation.",),
            decision_complete=False,
        )
    if not feasibility.feasible or feasibility.status_code is not FeasibilityStatus.FEASIBLE:
        return _empty_result(
            AllocationStatus.FEASIBILITY_NOT_CONFIRMED,
            "Gate 1 feasibility was not confirmed.",
            feasibility,
        )
    if (
        not isinstance(supplier_inputs, Sequence)
        or isinstance(supplier_inputs, (str, bytes))
        or not supplier_inputs
        or any(not isinstance(item, SupplierAllocationInput) for item in supplier_inputs)
    ):
        return _empty_result(
            AllocationStatus.INVALID_SUPPLIER_INPUT,
            "Every supplier input must be a normalized SupplierAllocationInput.",
            feasibility,
        )

    suppliers = sorted(supplier_inputs, key=lambda item: item.supplier_id)
    identifiers = [item.supplier_id for item in suppliers]
    if len(set(identifiers)) != len(identifiers):
        return _empty_result(
            AllocationStatus.INVALID_SUPPLIER_INPUT,
            "Duplicate supplier identifiers are not permitted.",
            feasibility,
        )
    by_id = {item.supplier_id: item for item in suppliers}
    eligible_ids = {
        item.supplier_id
        for item in suppliers
        if item.technical_eligible
        and item.risk_score >= request.minimum_risk_score
        and item.esg_score >= request.minimum_esg_score
        and item.supplier_id not in request.excluded_supplier_ids
    }
    evidence_ids = {str(item["supplier_id"]) for item in feasibility.supplier_capacity_evidence}
    if eligible_ids != evidence_ids:
        return _empty_result(
            AllocationStatus.SUPPLIER_UNIVERSE_MISMATCH,
            "Supplier universe differs from Gate 1 feasibility evidence.",
            feasibility,
        )

    mismatches = _evidence_mismatches(request, by_id, feasibility, eligible_ids)
    if mismatches:
        return _empty_result(
            AllocationStatus.FEASIBILITY_EVIDENCE_MISMATCH,
            "Gate 1 feasibility evidence does not reconcile with Gate 2 supplier inputs.",
            feasibility,
            warnings=mismatches,
        )

    maximum_shares = dict(feasibility.maximum_feasible_share_by_supplier)
    candidates: list[dict[str, Any]] = []
    for raw_portfolio in feasibility.feasible_supplier_combinations:
        portfolio = tuple(sorted(raw_portfolio))
        if len(portfolio) != request.required_awardee_count or any(sid not in by_id for sid in portfolio):
            continue
        allocations = _allocate_portfolio(request, portfolio, by_id, maximum_shares)
        if allocations is None:
            continue
        volumes = {sid: request.annual_volume * allocations[sid] / 100.0 for sid in portfolio}
        annual_tco = {sid: volumes[sid] * by_id[sid].adjusted_tco_unit_usd for sid in portfolio}
        utilization = {
            sid: volumes[sid] / float(by_id[sid].supplier_capacity) * 100.0
            for sid in portfolio
        }
        if not _final_invariants_hold(
            request,
            portfolio,
            allocations,
            maximum_shares,
            by_id,
            volumes,
            utilization,
        ):
            continue
        portfolio_tco = sum(annual_tco.values())
        hhi = sum((allocations[sid] / 100.0) ** 2 for sid in portfolio)
        weighted_performance = sum(
            allocations[sid] / 100.0 * by_id[sid].performance_score for sid in portfolio
        )
        weighted_esg = sum(allocations[sid] / 100.0 * by_id[sid].esg_score for sid in portfolio)
        aggregate_headroom = sum(maximum_shares[sid] - allocations[sid] for sid in portfolio)
        objective = (
            round(portfolio_tco, 8),
            round(hhi, 10),
            -min(by_id[sid].risk_score for sid in portfolio),
            -round(weighted_performance, 8),
            -round(weighted_esg, 8),
            -round(aggregate_headroom, 8),
            portfolio,
        )
        candidates.append(
            {
                "portfolio": portfolio,
                "allocations": allocations,
                "volumes": volumes,
                "annual_tco": annual_tco,
                "utilization": utilization,
                "portfolio_tco": portfolio_tco,
                "hhi": hhi,
                "weighted_performance": weighted_performance,
                "weighted_esg": weighted_esg,
                "aggregate_headroom": aggregate_headroom,
                "objective": objective,
            }
        )

    if not candidates:
        return _empty_result(
            AllocationStatus.NO_EXACT_ALLOCATION,
            "No exact 100% allocation satisfies all Gate 2 constraints.",
            feasibility,
        )
    chosen = min(candidates, key=lambda item: item["objective"])
    portfolio = chosen["portfolio"]
    allocations = chosen["allocations"]
    if not _final_invariants_hold(
        request,
        portfolio,
        allocations,
        maximum_shares,
        by_id,
        chosen["volumes"],
        chosen["utilization"],
    ):
        return _empty_result(
            AllocationStatus.NUMERIC_RECONCILIATION_FAILURE,
            "Final allocation invariants did not reconcile.",
            feasibility,
        )

    roles = _roles(portfolio, allocations, by_id, maximum_shares)
    ranking = sorted(
        portfolio,
        key=lambda sid: _remaining_headroom_key(by_id[sid], maximum_shares[sid], allocations[sid]),
    )
    inclusion = {
        sid: (
            "Technical and commercial eligibility confirmed.",
            f"Selected in the lowest governed feasible portfolio; governed rank {ranking.index(sid) + 1} of {len(portfolio)}.",
            f"Recommended allocation {allocations[sid]:.2f}% with role {roles[sid]}.",
            f"Unit TCO {by_id[sid].adjusted_tco_unit_usd:.6f} USD and total score {by_id[sid].total_score:.2f}.",
            f"Maximum feasible share {maximum_shares[sid]:.2f}%; capacity utilization {chosen['utilization'][sid]:.2f}%.",
        )
        for sid in portfolio
    }
    return MultiSupplierAllocationResult(
        contract_version=request.contract_version,
        allocation_engine_version=ALLOCATION_ENGINE_VERSION,
        feasible=True,
        decision_complete=True,
        status_code=AllocationStatus.ALLOCATION_RECOMMENDED,
        summary=f"Recommended exactly-{request.required_awardee_count} supplier allocation totals 100%.",
        selected_supplier_ids=portfolio,
        allocation_pct_by_supplier=dict(allocations),
        allocated_volume_by_supplier={sid: round(chosen["volumes"][sid], 8) for sid in portfolio},
        unit_tco_by_supplier={sid: by_id[sid].adjusted_tco_unit_usd for sid in portfolio},
        annual_tco_by_supplier={sid: round(chosen["annual_tco"][sid], 8) for sid in portfolio},
        portfolio_annual_tco=round(chosen["portfolio_tco"], 8),
        capacity_utilization_pct_by_supplier={
            sid: round(chosen["utilization"][sid], 8) for sid in portfolio
        },
        supplier_roles=roles,
        inclusion_reasons=inclusion,
        exclusion_reasons=_exclusion_reasons(request, suppliers, set(portfolio), maximum_shares),
        binding_constraints=(
            "exact awardee count",
            "100% reconciliation",
            "capacity ceiling",
            "continuity share",
            "minimum and maximum share",
        ),
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
