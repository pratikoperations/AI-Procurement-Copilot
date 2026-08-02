"""Canonical scenario-allocation boundary for Gate 3C1.

Scenario engines may transform source data and recalculate category scoring, but
allocation authority remains the accepted Gate 3A → Gate 1 → Gate 2 route. This
module contains no scenario transformation, supplier-selection or allocation
calculation logic and never falls back to legacy allocation functions.
"""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

import pandas as pd

from modules.multi_supplier_allocation_application import project_route_allocation
from modules.multi_supplier_allocation_route import (
    GovernedMultiSupplierAllocationRouteResult,
    RouteStatus,
    run_multi_supplier_allocation_route,
)

SCENARIO_ALLOCATION_VERSION = "AIPC-MULTI-ALLOC-SCENARIO-1.0"


def _freeze(value: Mapping[str, Any]) -> Mapping[str, Any]:
    return MappingProxyType(dict(value))


def _scenario_controls(assumptions: Mapping[str, Any], effective_annual_volume: float) -> dict[str, Any]:
    """Build explicit canonical controls without inferring missing supplier evidence."""
    return {
        "annual_volume": float(effective_annual_volume),
        "annual_volume_unit": str(
            assumptions.get("annual_volume_unit")
            or assumptions.get("category_profile", {}).get("unit")
            or assumptions.get("unit")
            or "unit"
        ),
        "required_awardee_count": int(assumptions.get("required_awardee_count", 2)),
        "minimum_awarded_share_pct": float(assumptions.get("minimum_awarded_share_pct", 10.0)),
        "maximum_supplier_share_pct": float(
            assumptions.get("max_supplier_share", assumptions.get("maximum_supplier_share_pct", 75.0))
        ),
        "minimum_continuity_share_pct": float(
            assumptions.get("min_backup_share", assumptions.get("minimum_continuity_share_pct", 25.0))
        ),
        "minimum_risk_score": float(assumptions.get("min_risk_score", 0.0)),
        "minimum_esg_score": float(assumptions.get("min_esg_score", 0.0)),
        "capacity_utilization_ceiling_pct": float(
            assumptions.get("capacity_utilization_ceiling_pct", 90.0)
        ),
        "category": str(assumptions.get("category") or ""),
        "commodity": str(assumptions.get("commodity") or ""),
        "comparison_currency": "USD",
        "required_supplier_ids": tuple(assumptions.get("required_supplier_ids", ())),
        "excluded_supplier_ids": tuple(assumptions.get("excluded_supplier_ids", ())),
    }


@dataclass(frozen=True, slots=True)
class ScenarioAllocationResult:
    scenario_allocation_version: str
    scenario_name: str
    scenario_applicable: bool
    scenario_assumption_version: str
    effective_annual_volume: float
    route_result: GovernedMultiSupplierAllocationRouteResult | None
    allocation_df: pd.DataFrame
    scenario_metadata: Mapping[str, Any]
    human_review_required: bool = True
    legacy_fallback_used: bool = False

    def __post_init__(self) -> None:
        if self.scenario_allocation_version != SCENARIO_ALLOCATION_VERSION:
            raise ValueError(f"Unsupported scenario_allocation_version '{self.scenario_allocation_version}'")
        if self.human_review_required is not True:
            raise ValueError("Human procurement review must remain mandatory")
        if self.legacy_fallback_used is not False:
            raise ValueError("Legacy scenario allocation fallback is prohibited")
        if not self.scenario_applicable and self.route_result is not None:
            raise ValueError("A non-applicable scenario must not invoke the allocation route")
        if self.route_result is not None:
            if self.route_result.human_review_required is not True:
                raise ValueError("Canonical route must retain human review")
            if self.route_result.legacy_fallback_used is not False:
                raise ValueError("Canonical route must prohibit legacy fallback")
            if self.route_result.allocation_result is None and not self.allocation_df.empty:
                raise ValueError("Blocked scenario routes cannot expose allocation rows")
        object.__setattr__(self, "allocation_df", self.allocation_df.copy(deep=True))
        object.__setattr__(self, "scenario_metadata", _freeze(self.scenario_metadata))

    @property
    def route_status(self) -> str:
        return self.route_result.route_status.value if self.route_result is not None else "NOT_APPLICABLE"

    @property
    def allocation_available(self) -> bool:
        return (
            self.route_result is not None
            and self.route_result.route_status in {RouteStatus.READY, RouteStatus.WARNING}
            and self.route_result.allocation_result is not None
            and not self.allocation_df.empty
        )

    def compatibility_allocation(self) -> dict[str, Any]:
        """Temporary Gate 3C1 shape for unchanged read-only scenario consumers."""
        route = self.route_result
        return {
            "allocation_df": self.allocation_df.copy(deep=True),
            "explanation": (
                route.route_summary
                if route is not None
                else "Scenario is not applicable; the canonical allocation route was not invoked."
            ),
            "route_status": self.route_status,
            "warnings": tuple(route.warnings) if route is not None else (),
            "blocking_reasons": tuple(route.blocking_reasons) if route is not None else (),
            "evidence_origin": route.evidence_origin if route is not None else "",
            "human_review_required": True,
            "legacy_fallback_used": False,
        }


def run_scenario_allocation(
    scored_df: pd.DataFrame,
    assumptions: Mapping[str, Any],
    *,
    scenario_name: str,
    effective_annual_volume: float,
    scenario_applicable: bool = True,
    scenario_assumption_version: str = "",
    scenario_metadata: Mapping[str, Any] | None = None,
    evidence_origin: str | None = None,
) -> ScenarioAllocationResult:
    """Run one applicable scenario through the canonical allocation route exactly once."""
    metadata = dict(scenario_metadata or {})
    if not scenario_applicable:
        return ScenarioAllocationResult(
            scenario_allocation_version=SCENARIO_ALLOCATION_VERSION,
            scenario_name=str(scenario_name),
            scenario_applicable=False,
            scenario_assumption_version=str(scenario_assumption_version),
            effective_annual_volume=float(effective_annual_volume),
            route_result=None,
            allocation_df=pd.DataFrame(),
            scenario_metadata=metadata,
            human_review_required=True,
            legacy_fallback_used=False,
        )

    controls = _scenario_controls(assumptions, effective_annual_volume)
    origin = str(evidence_origin or metadata.get("evidence_origin") or "controlled_synthetic")
    route_result = run_multi_supplier_allocation_route(
        scored_df,
        controls,
        route_name=f"scenario-gate-3c1:{scenario_name}",
        source_type="category_adapter",
        evidence_origin=origin,
    )
    allocation_df = project_route_allocation(route_result, scored_df)
    return ScenarioAllocationResult(
        scenario_allocation_version=SCENARIO_ALLOCATION_VERSION,
        scenario_name=str(scenario_name),
        scenario_applicable=True,
        scenario_assumption_version=str(scenario_assumption_version),
        effective_annual_volume=float(effective_annual_volume),
        route_result=route_result,
        allocation_df=allocation_df,
        scenario_metadata=metadata,
        human_review_required=True,
        legacy_fallback_used=False,
    )
