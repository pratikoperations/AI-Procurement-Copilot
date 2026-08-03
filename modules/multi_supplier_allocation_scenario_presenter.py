"""Governed presentation projection for canonical scenario allocation results.

This module is presentation-only. It never scores suppliers, evaluates feasibility,
selects suppliers, calculates allocation shares, or creates fallback allocations.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from modules.multi_supplier_allocation_scenario import ScenarioAllocationResult

SCENARIO_PRESENTER_VERSION = "AIPC-MULTI-ALLOC-SCENARIO-PRESENTER-1.0"


def _column(frame: pd.DataFrame, *candidates: str) -> str | None:
    return next((name for name in candidates if name in frame.columns), None)


def _text_list(values: list[Any]) -> str:
    cleaned = [str(value).strip() for value in values if str(value).strip()]
    return "; ".join(cleaned)


@dataclass(frozen=True, slots=True)
class ScenarioPresentation:
    presenter_version: str
    scenario: str
    scenario_applicable: bool
    scenario_assumption_version: str
    route_status: str
    status_reason: str
    evidence_origin: str
    human_review_required: bool
    legacy_fallback_used: bool
    allocation_available: bool
    allocation_df: pd.DataFrame
    selected_suppliers: tuple[str, ...]
    allocation_shares: tuple[str, ...]
    allocated_volumes: tuple[str, ...]
    primary_supplier: str
    continuity_supplier: str
    warnings: tuple[str, ...]
    blocking_reasons: tuple[str, ...]
    analytical_leading_supplier: str
    analytical_leading_score: float | None

    def __post_init__(self) -> None:
        if self.presenter_version != SCENARIO_PRESENTER_VERSION:
            raise ValueError("Unsupported scenario presenter version")
        if self.human_review_required is not True:
            raise ValueError("Human procurement review must remain mandatory")
        if self.legacy_fallback_used is not False:
            raise ValueError("Legacy scenario allocation fallback is prohibited")
        if not self.allocation_available and not self.allocation_df.empty:
            raise ValueError("Unavailable scenario allocation cannot expose rows")
        object.__setattr__(self, "allocation_df", self.allocation_df.copy(deep=True))

    def table_row(self) -> dict[str, Any]:
        return {
            "Scenario": self.scenario,
            "Scenario Applicable": self.scenario_applicable,
            "Scenario Assumption Version": self.scenario_assumption_version,
            "Scenario Route Status": self.route_status,
            "Scenario Status / Reason": self.status_reason,
            "Canonical Allocation Status": "Allocated" if self.allocation_available else "No allocation",
            "Allocation Available": self.allocation_available,
            "Selected Suppliers": _text_list(list(self.selected_suppliers)),
            "Allocation Shares": _text_list(list(self.allocation_shares)),
            "Allocated Volumes": _text_list(list(self.allocated_volumes)),
            "Primary Supplier": self.primary_supplier,
            "Continuity Supplier": self.continuity_supplier,
            "Evidence Origin": self.evidence_origin,
            "Human Review Required": "Yes",
            "Legacy Fallback Used": "No",
            "Warnings": _text_list(list(self.warnings)),
            "Blocking Reasons": _text_list(list(self.blocking_reasons)),
            "Analytical Leading Supplier": self.analytical_leading_supplier,
            "Analytical Leading Score": self.analytical_leading_score,
        }


def build_scenario_presentation(
    result: ScenarioAllocationResult,
    *,
    analytical_leading_supplier: str = "",
    analytical_leading_score: float | None = None,
    status_reason: str = "",
) -> ScenarioPresentation:
    """Project one immutable Gate 3C1 result for UI and table consumers."""
    route = result.route_result
    allocation = result.allocation_df.copy(deep=True) if result.allocation_available else pd.DataFrame()
    supplier_col = _column(allocation, "Supplier", "supplier", "supplier_id")
    share_col = _column(allocation, "Recommended Allocation %", "Allocation %", "allocation_pct")
    volume_col = _column(allocation, "Allocated Volume", "allocated_volume")
    role_col = _column(allocation, "Role", "Supplier Role", "role")

    selected = tuple(allocation[supplier_col].astype(str)) if supplier_col else ()
    shares = (
        tuple(f"{supplier}: {float(share):.2f}%" for supplier, share in zip(allocation[supplier_col], allocation[share_col]))
        if supplier_col and share_col else ()
    )
    volumes = (
        tuple(f"{supplier}: {float(volume):.2f}" for supplier, volume in zip(allocation[supplier_col], allocation[volume_col]))
        if supplier_col and volume_col else ()
    )
    primary = ""
    continuity = ""
    if supplier_col and role_col:
        for _, row in allocation.iterrows():
            role = str(row[role_col]).strip().casefold()
            supplier = str(row[supplier_col]).strip()
            if role == "primary":
                primary = supplier
            elif role in {"continuity", "backup", "secondary"}:
                continuity = supplier

    if not status_reason:
        if not result.scenario_applicable:
            status_reason = str(result.scenario_metadata.get("reason") or "Scenario is not applicable.")
        elif route is not None:
            status_reason = route.route_summary
        else:
            status_reason = "; ".join(result.integration_blocking_reasons)

    return ScenarioPresentation(
        presenter_version=SCENARIO_PRESENTER_VERSION,
        scenario=result.scenario_name,
        scenario_applicable=result.scenario_applicable,
        scenario_assumption_version=result.scenario_assumption_version,
        route_status=result.route_status,
        status_reason=str(status_reason),
        evidence_origin=route.evidence_origin if route is not None else "",
        human_review_required=True,
        legacy_fallback_used=False,
        allocation_available=result.allocation_available,
        allocation_df=allocation,
        selected_suppliers=selected,
        allocation_shares=shares,
        allocated_volumes=volumes,
        primary_supplier=primary,
        continuity_supplier=continuity,
        warnings=tuple(route.warnings) if route is not None else (),
        blocking_reasons=(
            tuple(route.blocking_reasons)
            if route is not None
            else tuple(result.integration_blocking_reasons)
        ),
        analytical_leading_supplier=str(analytical_leading_supplier or ""),
        analytical_leading_score=(
            None if analytical_leading_score is None else float(analytical_leading_score)
        ),
    )
