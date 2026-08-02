"""Canonical governed orchestration for multi-supplier allocation.

This module is intentionally isolated from the Streamlit application. It invokes
only the accepted Gate 3A adapter, Gate 1 feasibility evaluator and Gate 2
exactly-K allocation engine. It never invokes legacy allocation functions.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
from types import MappingProxyType
from typing import Any, Mapping

import pandas as pd

from modules.allocation_contract import FeasibilityStatus, MultiSupplierFeasibilityResult
from modules.allocation_feasibility import evaluate_allocation_feasibility
from modules.multi_supplier_allocation import (
    ALLOCATION_ENGINE_VERSION,
    AllocationStatus,
    MultiSupplierAllocationResult,
    recommend_multi_supplier_allocation,
)
from modules.multi_supplier_allocation_adapter import (
    AdapterStatus,
    MultiSupplierAllocationAdapterResult,
    build_multi_supplier_allocation_adapter,
)

ROUTE_VERSION = "AIPC-MULTI-ALLOC-ROUTE-1.0"
PARTIAL_EVIDENCE_LABEL = "Partial evidence captured before adapter failure"


class RouteStatus(str, Enum):
    READY = "READY"
    WARNING = "WARNING"
    BLOCKED_INVALID_INPUT = "BLOCKED_INVALID_INPUT"
    BLOCKED_MISSING_ELIGIBILITY = "BLOCKED_MISSING_ELIGIBILITY"
    BLOCKED_MISSING_CAPACITY = "BLOCKED_MISSING_CAPACITY"
    BLOCKED_INFEASIBLE = "BLOCKED_INFEASIBLE"
    BLOCKED_INDETERMINATE = "BLOCKED_INDETERMINATE"
    BLOCKED_ADAPTER_FAILURE = "BLOCKED_ADAPTER_FAILURE"
    BLOCKED_ENGINE_FAILURE = "BLOCKED_ENGINE_FAILURE"


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType(
            {str(key): _freeze(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))}
        )
    if isinstance(value, (list, tuple, set, frozenset)):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, Enum):
        return value.value
    return value


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _thaw(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    if isinstance(value, Enum):
        return value.value
    return value


def _result_payload(value: Any) -> Any:
    if value is None:
        return None
    if hasattr(value, "to_dict"):
        return value.to_dict()
    raise TypeError(f"Unsupported governed route payload type: {type(value).__name__}")


@dataclass(frozen=True, slots=True)
class GovernedMultiSupplierAllocationRouteResult:
    route_version: str
    route_status: RouteStatus
    route_summary: str
    source_type: str
    evidence_origin: str
    adapter_result: MultiSupplierAllocationAdapterResult | None
    feasibility_result: MultiSupplierFeasibilityResult | None
    allocation_result: MultiSupplierAllocationResult | None
    blocking_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    partial_evidence: Mapping[str, Any]
    human_review_required: bool = True
    legacy_fallback_used: bool = False

    def __post_init__(self) -> None:
        if self.route_version != ROUTE_VERSION:
            raise ValueError(f"Unsupported route_version '{self.route_version}'")
        if not isinstance(self.route_status, RouteStatus):
            raise TypeError("route_status must be a RouteStatus")
        if self.human_review_required is not True:
            raise ValueError("Human procurement review must remain mandatory")
        if self.legacy_fallback_used is not False:
            raise ValueError("Legacy allocation fallback is prohibited")
        if self.route_status not in {RouteStatus.READY, RouteStatus.WARNING} and self.allocation_result is not None:
            raise ValueError("Blocked route results cannot contain an allocation recommendation")
        if self.allocation_result is not None and self.allocation_result.allocation_engine_version != ALLOCATION_ENGINE_VERSION:
            raise ValueError("The canonical route accepts only the governed Gate 2 engine result")
        object.__setattr__(self, "blocking_reasons", tuple(sorted(set(str(item) for item in self.blocking_reasons))))
        object.__setattr__(self, "warnings", tuple(sorted(set(str(item) for item in self.warnings))))
        object.__setattr__(self, "partial_evidence", _freeze(dict(self.partial_evidence or {})))

    def to_dict(self) -> dict[str, Any]:
        return {
            "route_version": self.route_version,
            "route_status": self.route_status.value,
            "route_summary": self.route_summary,
            "source_type": self.source_type,
            "evidence_origin": self.evidence_origin,
            "adapter_result": _result_payload(self.adapter_result),
            "feasibility_result": _result_payload(self.feasibility_result),
            "allocation_result": _result_payload(self.allocation_result),
            "blocking_reasons": list(self.blocking_reasons),
            "warnings": list(self.warnings),
            "partial_evidence": _thaw(self.partial_evidence),
            "human_review_required": self.human_review_required,
            "legacy_fallback_used": self.legacy_fallback_used,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"), allow_nan=False)


def _origin_from_adapter(adapter: MultiSupplierAllocationAdapterResult | None, supplied_origin: str | None) -> str:
    if adapter is not None:
        for evidence_group in (adapter.eligibility_evidence, adapter.capacity_evidence):
            for item in evidence_group:
                origin = str(item.get("evidence_origin") or "").strip()
                if origin:
                    return origin
        for supplier in adapter.supplier_inputs:
            origin = str(supplier.category_specific_eligibility_evidence.get("evidence_origin") or "").strip()
            if origin:
                return origin
    return str(supplied_origin or "").strip()


def _partial_evidence(adapter: MultiSupplierAllocationAdapterResult | None) -> Mapping[str, Any]:
    if adapter is None:
        return {}
    evidence = {
        "field_provenance": [dict(item) for item in adapter.field_provenance],
        "eligibility_evidence": [dict(item) for item in adapter.eligibility_evidence],
        "capacity_evidence": [dict(item) for item in adapter.capacity_evidence],
        "supplier_inputs": [
            {
                "supplier_id": item.supplier_id,
                "technical_eligible": item.technical_eligible,
                "category_specific_eligibility_evidence": _thaw(item.category_specific_eligibility_evidence),
            }
            for item in adapter.supplier_inputs
        ],
    }
    return evidence if any(evidence.values()) else {}


def _feasibility_records(adapter: MultiSupplierAllocationAdapterResult) -> tuple[Mapping[str, Any], ...]:
    """Project immutable adapter inputs into Gate 1's accepted mapping boundary."""
    return tuple(
        {
            "supplier_id": item.supplier_id,
            "technical_eligible": item.technical_eligible,
            "adjusted_tco_unit_usd": item.adjusted_tco_unit_usd,
            "total_score": item.total_score,
            "risk_score": item.risk_score,
            "performance_score": item.performance_score,
            "esg_score": item.esg_score,
            "supplier_capacity": item.supplier_capacity,
            "eligibility_failure_reasons": tuple(item.eligibility_failure_reasons),
            "category_specific_eligibility_evidence": _thaw(item.category_specific_eligibility_evidence),
        }
        for item in adapter.supplier_inputs
    )


def _adapter_block_status(status: AdapterStatus) -> RouteStatus:
    if status in {AdapterStatus.MISSING_TECHNICAL_ELIGIBILITY, AdapterStatus.AMBIGUOUS_TECHNICAL_ELIGIBILITY}:
        return RouteStatus.BLOCKED_MISSING_ELIGIBILITY
    if status in {AdapterStatus.MISSING_SUPPLIER_CAPACITY, AdapterStatus.INVALID_SUPPLIER_CAPACITY}:
        return RouteStatus.BLOCKED_MISSING_CAPACITY
    if status is AdapterStatus.CONTRACT_CONSTRUCTION_FAILURE:
        return RouteStatus.BLOCKED_ADAPTER_FAILURE
    return RouteStatus.BLOCKED_INVALID_INPUT


def _blocked_adapter_result(
    adapter: MultiSupplierAllocationAdapterResult,
    supplied_origin: str | None,
) -> GovernedMultiSupplierAllocationRouteResult:
    partial = _partial_evidence(adapter)
    summary = PARTIAL_EVIDENCE_LABEL if partial else adapter.summary
    warnings = list(adapter.warnings)
    if partial:
        warnings.append(PARTIAL_EVIDENCE_LABEL)
    return GovernedMultiSupplierAllocationRouteResult(
        route_version=ROUTE_VERSION,
        route_status=_adapter_block_status(adapter.status_code),
        route_summary=summary,
        source_type=adapter.source_type,
        evidence_origin=_origin_from_adapter(adapter, supplied_origin),
        adapter_result=adapter,
        feasibility_result=None,
        allocation_result=None,
        blocking_reasons=adapter.blocking_reasons,
        warnings=tuple(warnings),
        partial_evidence=partial,
        human_review_required=True,
        legacy_fallback_used=False,
    )


def _blocked_feasibility_result(
    adapter: MultiSupplierAllocationAdapterResult,
    feasibility: MultiSupplierFeasibilityResult,
    supplied_origin: str | None,
) -> GovernedMultiSupplierAllocationRouteResult:
    indeterminate = (
        not feasibility.decision_complete
        or feasibility.status_code is FeasibilityStatus.ENUMERATION_LIMIT_REACHED
    )
    return GovernedMultiSupplierAllocationRouteResult(
        route_version=ROUTE_VERSION,
        route_status=RouteStatus.BLOCKED_INDETERMINATE if indeterminate else RouteStatus.BLOCKED_INFEASIBLE,
        route_summary=feasibility.summary,
        source_type=adapter.source_type,
        evidence_origin=_origin_from_adapter(adapter, supplied_origin),
        adapter_result=adapter,
        feasibility_result=feasibility,
        allocation_result=None,
        blocking_reasons=feasibility.blocking_reasons,
        warnings=tuple(adapter.warnings) + tuple(feasibility.warnings),
        partial_evidence={},
        human_review_required=True,
        legacy_fallback_used=False,
    )


def run_multi_supplier_allocation_route(
    scored_df: pd.DataFrame,
    controls: Mapping[str, Any],
    *,
    route_name: str,
    source_type: str,
    column_aliases: Mapping[str, str] | None = None,
    evidence_origin: str | None = None,
    max_combinations: int = 5000,
) -> GovernedMultiSupplierAllocationRouteResult:
    """Run the canonical adapter → feasibility → exactly-K engine sequence."""
    try:
        adapter = build_multi_supplier_allocation_adapter(
            scored_df,
            controls,
            route_name=route_name,
            source_type=source_type,
            column_aliases=column_aliases,
            evidence_origin=evidence_origin,
        )
    except Exception as exc:  # governed boundary: never fall back to legacy allocation
        return GovernedMultiSupplierAllocationRouteResult(
            route_version=ROUTE_VERSION,
            route_status=RouteStatus.BLOCKED_ADAPTER_FAILURE,
            route_summary="The governed allocation adapter failed; no allocation was attempted.",
            source_type=str(source_type or ""),
            evidence_origin=str(evidence_origin or ""),
            adapter_result=None,
            feasibility_result=None,
            allocation_result=None,
            blocking_reasons=(f"Adapter raised {type(exc).__name__}",),
            warnings=(),
            partial_evidence={},
            human_review_required=True,
            legacy_fallback_used=False,
        )

    if not adapter.ready:
        return _blocked_adapter_result(adapter, evidence_origin)
    if adapter.request is None:
        return GovernedMultiSupplierAllocationRouteResult(
            route_version=ROUTE_VERSION,
            route_status=RouteStatus.BLOCKED_ADAPTER_FAILURE,
            route_summary="The adapter reported readiness without a governed request.",
            source_type=adapter.source_type,
            evidence_origin=_origin_from_adapter(adapter, evidence_origin),
            adapter_result=adapter,
            feasibility_result=None,
            allocation_result=None,
            blocking_reasons=("Ready adapter result must contain a governed allocation request",),
            warnings=adapter.warnings,
            partial_evidence=_partial_evidence(adapter),
            human_review_required=True,
            legacy_fallback_used=False,
        )

    try:
        feasibility = evaluate_allocation_feasibility(
            adapter.request,
            _feasibility_records(adapter),
            max_combinations=max_combinations,
        )
    except Exception as exc:
        return GovernedMultiSupplierAllocationRouteResult(
            route_version=ROUTE_VERSION,
            route_status=RouteStatus.BLOCKED_ENGINE_FAILURE,
            route_summary="Governed feasibility evaluation failed; no allocation was attempted.",
            source_type=adapter.source_type,
            evidence_origin=_origin_from_adapter(adapter, evidence_origin),
            adapter_result=adapter,
            feasibility_result=None,
            allocation_result=None,
            blocking_reasons=(f"Feasibility evaluator raised {type(exc).__name__}",),
            warnings=adapter.warnings,
            partial_evidence={},
            human_review_required=True,
            legacy_fallback_used=False,
        )

    if not feasibility.feasible or feasibility.status_code is not FeasibilityStatus.FEASIBLE:
        return _blocked_feasibility_result(adapter, feasibility, evidence_origin)

    try:
        allocation = recommend_multi_supplier_allocation(
            adapter.request,
            adapter.supplier_inputs,
            feasibility,
        )
    except Exception as exc:
        return GovernedMultiSupplierAllocationRouteResult(
            route_version=ROUTE_VERSION,
            route_status=RouteStatus.BLOCKED_ENGINE_FAILURE,
            route_summary="The governed allocation engine failed; no recommendation is available.",
            source_type=adapter.source_type,
            evidence_origin=_origin_from_adapter(adapter, evidence_origin),
            adapter_result=adapter,
            feasibility_result=feasibility,
            allocation_result=None,
            blocking_reasons=(f"Allocation engine raised {type(exc).__name__}",),
            warnings=tuple(adapter.warnings) + tuple(feasibility.warnings),
            partial_evidence={},
            human_review_required=True,
            legacy_fallback_used=False,
        )

    if allocation.status_code is not AllocationStatus.ALLOCATION_RECOMMENDED:
        indeterminate = allocation.status_code is AllocationStatus.FEASIBILITY_INDETERMINATE
        infeasible = allocation.status_code in {
            AllocationStatus.FEASIBILITY_NOT_CONFIRMED,
            AllocationStatus.NO_EXACT_ALLOCATION,
        }
        status = (
            RouteStatus.BLOCKED_INDETERMINATE
            if indeterminate
            else RouteStatus.BLOCKED_INFEASIBLE
            if infeasible
            else RouteStatus.BLOCKED_ENGINE_FAILURE
        )
        return GovernedMultiSupplierAllocationRouteResult(
            route_version=ROUTE_VERSION,
            route_status=status,
            route_summary=allocation.summary,
            source_type=adapter.source_type,
            evidence_origin=_origin_from_adapter(adapter, evidence_origin),
            adapter_result=adapter,
            feasibility_result=feasibility,
            allocation_result=None,
            blocking_reasons=(allocation.summary,),
            warnings=tuple(adapter.warnings) + tuple(feasibility.warnings) + tuple(allocation.warnings),
            partial_evidence={},
            human_review_required=True,
            legacy_fallback_used=False,
        )

    warnings = tuple(adapter.warnings) + tuple(feasibility.warnings) + tuple(allocation.warnings)
    return GovernedMultiSupplierAllocationRouteResult(
        route_version=ROUTE_VERSION,
        route_status=RouteStatus.WARNING if warnings else RouteStatus.READY,
        route_summary=allocation.summary,
        source_type=adapter.source_type,
        evidence_origin=_origin_from_adapter(adapter, evidence_origin),
        adapter_result=adapter,
        feasibility_result=feasibility,
        allocation_result=allocation,
        blocking_reasons=(),
        warnings=warnings,
        partial_evidence={},
        human_review_required=True,
        legacy_fallback_used=False,
    )
