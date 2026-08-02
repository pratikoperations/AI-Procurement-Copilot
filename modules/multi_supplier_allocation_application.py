"""Application integration and read-only presentation for the canonical allocation route.

This module is the Gate 3B2 boundary between the canonical route and application
consumers. It constructs explicit governed controls, invokes the accepted route
exactly once, and projects the exact Gate 2 result into the legacy-compatible
dataframe shape required by existing read-only consumers. It never calculates
supplier selection, eligibility, ranking or allocation.
"""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

import pandas as pd

from modules.multi_supplier_allocation_route import (
    GovernedMultiSupplierAllocationRouteResult,
    RouteStatus,
    run_multi_supplier_allocation_route,
)

APPLICATION_INTEGRATION_VERSION = "AIPC-MULTI-ALLOC-APP-1.0"
ALLOCATION_COLUMNS = (
    "Supplier",
    "Recommended Allocation %",
    "Role",
    "Advanced TCO Unit USD",
    "Estimated Annual TCO USD",
    "Allocated Volume",
    "Capacity Utilization %",
    "Reason",
    "Evidence Origin",
    "Route Status",
)


def _freeze(value: Mapping[str, Any]) -> Mapping[str, Any]:
    return MappingProxyType(dict(value))


@dataclass(frozen=True, slots=True)
class ApplicationAllocationBundle:
    integration_version: str
    route_result: GovernedMultiSupplierAllocationRouteResult
    allocation_df: pd.DataFrame
    intelligence_allocation: Mapping[str, Any]
    control_summary: Mapping[str, Any]
    scenario_allocation_deferred: bool = True

    def __post_init__(self) -> None:
        if self.integration_version != APPLICATION_INTEGRATION_VERSION:
            raise ValueError(f"Unsupported integration_version '{self.integration_version}'")
        if self.route_result.human_review_required is not True:
            raise ValueError("Human procurement review must remain mandatory")
        if self.route_result.legacy_fallback_used is not False:
            raise ValueError("Legacy allocation fallback is prohibited")
        object.__setattr__(self, "allocation_df", self.allocation_df.copy(deep=True))
        object.__setattr__(self, "intelligence_allocation", _freeze(self.intelligence_allocation))
        object.__setattr__(self, "control_summary", _freeze(self.control_summary))


def resolve_application_source_type(assumptions: Mapping[str, Any]) -> tuple[str, str | None]:
    """Resolve the governed adapter source and evidence origin without inference."""
    data_source = str(assumptions.get("data_source") or "Synthetic Demo")
    category = str(assumptions.get("category") or "")
    commodity = str(assumptions.get("commodity") or "")
    if data_source == "Governed v1.3 Workbook Review Preview":
        return "governed_workbook", "governed_workbook"
    if data_source == "Upload RFQ CSV/Excel":
        return "uploaded_rfq", "supplied"
    if category == "Raw Material Procurement" and commodity == "Steel":
        return "steel_synthetic", "controlled_synthetic"
    return "synthetic_demo", "controlled_synthetic"


def build_application_route_controls(assumptions: Mapping[str, Any]) -> dict[str, Any]:
    """Return explicit Gate 1 controls from visible or disclosed application values."""
    return {
        "annual_volume": float(assumptions["annual_volume"]),
        "annual_volume_unit": str(assumptions["annual_volume_unit"]),
        "required_awardee_count": int(assumptions.get("required_awardee_count", 2)),
        "minimum_awarded_share_pct": float(assumptions.get("minimum_awarded_share_pct", 10.0)),
        "maximum_supplier_share_pct": float(assumptions["max_supplier_share"]),
        "minimum_continuity_share_pct": float(assumptions["min_backup_share"]),
        "minimum_risk_score": float(assumptions["min_risk_score"]),
        "minimum_esg_score": float(assumptions["min_esg_score"]),
        "capacity_utilization_ceiling_pct": float(
            assumptions.get("capacity_utilization_ceiling_pct", 90.0)
        ),
        "category": str(assumptions["category"]),
        "commodity": str(assumptions["commodity"]),
        "comparison_currency": "USD",
        "required_supplier_ids": tuple(assumptions.get("required_supplier_ids", ())),
        "excluded_supplier_ids": tuple(assumptions.get("excluded_supplier_ids", ())),
    }


def _supplier_name_lookup(scored_df: pd.DataFrame) -> dict[str, str]:
    if "Supplier" not in scored_df.columns:
        return {}
    return {
        str(value).strip().casefold(): str(value).strip()
        for value in scored_df["Supplier"].tolist()
        if str(value).strip()
    }


def project_route_allocation(
    route_result: GovernedMultiSupplierAllocationRouteResult,
    scored_df: pd.DataFrame,
) -> pd.DataFrame:
    """Project the exact Gate 2 result into a read-only application dataframe."""
    allocation = route_result.allocation_result
    if allocation is None:
        return pd.DataFrame(columns=ALLOCATION_COLUMNS)

    names = _supplier_name_lookup(scored_df)
    rows: list[dict[str, Any]] = []
    for supplier_id in allocation.selected_supplier_ids:
        inclusion = allocation.inclusion_reasons.get(supplier_id, ())
        rows.append(
            {
                "Supplier": names.get(supplier_id, supplier_id),
                "Recommended Allocation %": allocation.allocation_pct_by_supplier[supplier_id],
                "Role": allocation.supplier_roles[supplier_id],
                "Advanced TCO Unit USD": allocation.unit_tco_by_supplier[supplier_id],
                "Estimated Annual TCO USD": allocation.annual_tco_by_supplier[supplier_id],
                "Allocated Volume": allocation.allocated_volume_by_supplier[supplier_id],
                "Capacity Utilization %": allocation.capacity_utilization_pct_by_supplier[supplier_id],
                "Reason": "; ".join(inclusion),
                "Evidence Origin": route_result.evidence_origin,
                "Route Status": route_result.route_status.value,
            }
        )
    return pd.DataFrame(rows, columns=ALLOCATION_COLUMNS)


def build_intelligence_allocation(
    route_result: GovernedMultiSupplierAllocationRouteResult,
    allocation_df: pd.DataFrame,
) -> dict[str, Any]:
    """Build a compatibility presentation object from the same canonical result."""
    return {
        "allocation_df": allocation_df.copy(deep=True),
        "explanation": route_result.route_summary,
        "route_status": route_result.route_status.value,
        "warnings": tuple(route_result.warnings),
        "blocking_reasons": tuple(route_result.blocking_reasons),
        "evidence_origin": route_result.evidence_origin,
        "human_review_required": True,
        "legacy_fallback_used": False,
    }


def route_allows_allocation(route_result: GovernedMultiSupplierAllocationRouteResult) -> bool:
    """Return whether the canonical route permits recommendation-bearing allocation use."""
    return (
        route_result.route_status in {RouteStatus.READY, RouteStatus.WARNING}
        and route_result.allocation_result is not None
    )


def build_route_decision_control(
    route_result: GovernedMultiSupplierAllocationRouteResult,
    eligibility: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Combine canonical route state and eligibility into one fail-closed UI control."""
    route_allowed = route_allows_allocation(route_result)
    eligibility_recommendation = bool(eligibility.get("recommendation_allowed", False))
    eligibility_final_award = bool(eligibility.get("final_award_language_allowed", False))
    recommendation_allowed = route_allowed and eligibility_recommendation
    final_award_allowed = route_allowed and eligibility_final_award
    if not route_allowed:
        message = (
            "Canonical allocation is unavailable. Cost, risk, scoring and supplier analysis remain "
            "analytical only; no supplier award or allocation recommendation is permitted."
        )
    elif not eligibility_recommendation:
        message = "Allocation exists, but validation controls withhold recommendation language."
    else:
        message = "Canonical allocation is available for human procurement review."
    return _freeze(
        {
            "route_allows_allocation": route_allowed,
            "eligibility_allows_recommendation": eligibility_recommendation,
            "eligibility_allows_final_award": eligibility_final_award,
            "recommendation_language_allowed": recommendation_allowed,
            "final_award_language_allowed": final_award_allowed,
            "analytical_only": not recommendation_allowed,
            "message": message,
        }
    )


def _display_supplier_ids(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "None"


def run_application_allocation(
    scored_df: pd.DataFrame,
    assumptions: Mapping[str, Any],
) -> ApplicationAllocationBundle:
    """Invoke the canonical route once and prepare all application consumers."""
    controls = build_application_route_controls(assumptions)
    source_type, evidence_origin = resolve_application_source_type(assumptions)
    route_result = run_multi_supplier_allocation_route(
        scored_df,
        controls,
        route_name="application-gate-3b2",
        source_type=source_type,
        evidence_origin=evidence_origin,
    )
    allocation_df = project_route_allocation(route_result, scored_df)
    return ApplicationAllocationBundle(
        integration_version=APPLICATION_INTEGRATION_VERSION,
        route_result=route_result,
        allocation_df=allocation_df,
        intelligence_allocation=build_intelligence_allocation(route_result, allocation_df),
        control_summary={
            "Required awardees": controls["required_awardee_count"],
            "Minimum awarded share %": controls["minimum_awarded_share_pct"],
            "Maximum supplier share %": controls["maximum_supplier_share_pct"],
            "Minimum continuity share %": controls["minimum_continuity_share_pct"],
            "Minimum risk score": controls["minimum_risk_score"],
            "Minimum ESG score": controls["minimum_esg_score"],
            "Capacity utilization ceiling %": controls["capacity_utilization_ceiling_pct"],
            "Required supplier IDs": _display_supplier_ids(controls["required_supplier_ids"]),
            "Excluded supplier IDs": _display_supplier_ids(controls["excluded_supplier_ids"]),
            "Comparison currency": controls["comparison_currency"],
            "Evidence origin": route_result.evidence_origin or "Not available",
            "Human review required": route_result.human_review_required,
            "Legacy fallback used": route_result.legacy_fallback_used,
        },
        scenario_allocation_deferred=True,
    )
