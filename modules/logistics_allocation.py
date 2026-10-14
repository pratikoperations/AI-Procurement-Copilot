"""Governed LOGISTICS-3 carrier allocation and scenario analysis.

LOGISTICS-3 evaluates explicit human-proposed FTL carrier allocations. It does
not select carriers, rank carriers, optimize an award, or write allocations to
TMS/ERP systems.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from modules.logistics_engine import CATEGORY_NAME, ENGINE_STATUS, FIRST_COMMODITY

ALLOCATION_SCENARIO_VERSION = "LOGISTICS-3"

ALLOCATION_SCENARIO_CONTRACT = {
    "contract_version": ALLOCATION_SCENARIO_VERSION,
    "required_carrier_fields": (
        "carrier_id",
        "carrier_name",
        "performance_status",
        "landed_freight_inr_per_trip",
        "available_capacity_trips",
        "proposed_allocation_pct",
        "source_label",
    ),
    "accepted_performance_statuses": (
        "MEETS_BUYER_POLICY_FOR_HUMAN_REVIEW",
        "MEETS_POLICY_WITH_UNVERIFIED_EVIDENCE",
    ),
    "governance_note": (
        "Allocations are human-proposed inputs. LOGISTICS-3 validates feasibility "
        "and computes scenario consequences; it does not select carriers, rank them, "
        "optimize shares, or create an award recommendation."
    ),
}


def _finite_number(
    name: str,
    value: Any,
    *,
    positive: bool = False,
    non_negative: bool = False,
) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric.") from exc
    if not math.isfinite(numeric):
        raise ValueError(f"{name} must be finite.")
    if positive and numeric <= 0:
        raise ValueError(f"{name} must be greater than zero.")
    if non_negative and numeric < 0:
        raise ValueError(f"{name} must be zero or greater.")
    return numeric


def get_allocation_scenario_profile() -> dict[str, Any]:
    """Return the bounded LOGISTICS-3 allocation/scenario contract."""
    return {
        "category": CATEGORY_NAME,
        "service": FIRST_COMMODITY,
        "engine_status": ENGINE_STATUS,
        "contract_version": ALLOCATION_SCENARIO_VERSION,
        "contract": dict(ALLOCATION_SCENARIO_CONTRACT),
        "human_proposed_allocation_required": True,
        "carrier_selection_enabled": False,
        "carrier_ranking_enabled": False,
        "automatic_share_optimization_enabled": False,
        "autonomous_award_enabled": False,
        "human_approval_required": True,
    }


def evaluate_allocation_scenario(
    *,
    annual_trip_demand: Any,
    carriers: Sequence[Mapping[str, Any]],
    scenario_name: str = "Base Case",
    demand_change_pct: Any = 0.0,
) -> dict[str, Any]:
    """Evaluate one explicit carrier allocation under one demand scenario."""
    demand = _finite_number("Annual trip demand", annual_trip_demand, positive=True)
    change_pct = _finite_number("Demand change percent", demand_change_pct)
    if change_pct <= -100:
        raise ValueError("Demand change percent must be greater than -100.")

    scenario_name_clean = str(scenario_name or "").strip()
    if not scenario_name_clean:
        raise ValueError("scenario_name is required.")
    if (
        not isinstance(carriers, Sequence)
        or isinstance(carriers, (str, bytes))
        or not carriers
    ):
        raise ValueError("At least one carrier allocation input is required.")

    effective_demand = demand * (1.0 + change_pct / 100.0)
    accepted_statuses = set(ALLOCATION_SCENARIO_CONTRACT["accepted_performance_statuses"])

    seen_ids: set[str] = set()
    allocation_rows: list[dict[str, Any]] = []
    blocking_reasons: list[str] = []
    review_reasons: list[str] = []
    total_share = 0.0
    portfolio_cost = 0.0

    for index, carrier in enumerate(carriers, start=1):
        missing = [
            field
            for field in ALLOCATION_SCENARIO_CONTRACT["required_carrier_fields"]
            if field not in carrier or carrier.get(field) is None
        ]
        if missing:
            raise ValueError(
                f"Carrier {index} missing required fields: " + ", ".join(missing)
            )

        carrier_id = str(carrier["carrier_id"]).strip()
        carrier_name = str(carrier["carrier_name"]).strip()
        status = str(carrier["performance_status"]).strip()
        source_label = str(carrier["source_label"]).strip()
        if not carrier_id:
            raise ValueError(f"Carrier {index} carrier_id is required.")
        if not carrier_name:
            raise ValueError(f"Carrier {index} carrier_name is required.")
        if not source_label:
            raise ValueError(f"Carrier {index} source_label is required.")
        if carrier_id in seen_ids:
            raise ValueError(f"Duplicate carrier_id: {carrier_id}")
        seen_ids.add(carrier_id)

        freight_per_trip = _finite_number(
            f"{carrier_id} landed freight INR/trip",
            carrier["landed_freight_inr_per_trip"],
            non_negative=True,
        )
        capacity_trips = _finite_number(
            f"{carrier_id} available capacity trips",
            carrier["available_capacity_trips"],
            non_negative=True,
        )
        share_pct = _finite_number(
            f"{carrier_id} proposed allocation percent",
            carrier["proposed_allocation_pct"],
            non_negative=True,
        )
        if share_pct > 100:
            raise ValueError(f"{carrier_id} proposed allocation percent must not exceed 100.")

        allocated_trips = effective_demand * share_pct / 100.0
        capacity_headroom = capacity_trips - allocated_trips
        capacity_feasible = capacity_headroom >= -1e-9
        performance_eligible = status in accepted_statuses
        carrier_cost = allocated_trips * freight_per_trip

        total_share += share_pct
        portfolio_cost += carrier_cost

        if not performance_eligible and share_pct > 0:
            blocking_reasons.append(
                f"{carrier_id}: performance status {status} is not eligible for positive allocation."
            )
        if not capacity_feasible and share_pct > 0:
            blocking_reasons.append(
                f"{carrier_id}: proposed allocation exceeds explicit available capacity by "
                f"{abs(capacity_headroom):.6g} trips."
            )
        if status == "MEETS_POLICY_WITH_UNVERIFIED_EVIDENCE" and share_pct > 0:
            review_reasons.append(
                f"{carrier_id}: positive allocation uses unverified performance evidence."
            )

        allocation_rows.append(
            {
                "carrier_id": carrier_id,
                "carrier_name": carrier_name,
                "performance_status": status,
                "source_label": source_label,
                "landed_freight_inr_per_trip": freight_per_trip,
                "available_capacity_trips": capacity_trips,
                "proposed_allocation_pct": share_pct,
                "allocated_trips": allocated_trips,
                "capacity_headroom_trips": capacity_headroom,
                "capacity_feasible": capacity_feasible,
                "performance_eligible": performance_eligible,
                "annual_freight_cost_inr": carrier_cost,
            }
        )

    if not math.isclose(total_share, 100.0, rel_tol=1e-9, abs_tol=1e-7):
        blocking_reasons.append(
            f"Proposed allocation must total 100%; received {total_share:.6g}%."
        )

    allocated_total = sum(row["allocated_trips"] for row in allocation_rows)
    if math.isclose(total_share, 100.0, rel_tol=1e-9, abs_tol=1e-7) and not math.isclose(
        allocated_total, effective_demand, rel_tol=1e-9, abs_tol=1e-7
    ):
        blocking_reasons.append("Allocated trip volume does not reconcile to scenario demand.")

    if blocking_reasons:
        status = "SCENARIO_INFEASIBLE"
    elif review_reasons:
        status = "SCENARIO_FEASIBLE_WITH_REVIEW"
    else:
        status = "SCENARIO_FEASIBLE_FOR_HUMAN_REVIEW"

    weighted_cost_per_trip = (
        portfolio_cost / effective_demand if effective_demand > 0 else 0.0
    )

    return {
        "contract_version": ALLOCATION_SCENARIO_VERSION,
        "category": CATEGORY_NAME,
        "service": FIRST_COMMODITY,
        "scenario_name": scenario_name_clean,
        "base_annual_trip_demand": demand,
        "demand_change_pct": change_pct,
        "effective_annual_trip_demand": effective_demand,
        "status": status,
        "allocation_rows": allocation_rows,
        "proposed_allocation_total_pct": total_share,
        "allocated_trip_total": allocated_total,
        "portfolio_annual_freight_cost_inr": portfolio_cost,
        "weighted_freight_cost_inr_per_trip": weighted_cost_per_trip,
        "blocking_reasons": blocking_reasons,
        "review_reasons": review_reasons,
        "carrier_selection_performed": False,
        "carrier_ranking_performed": False,
        "automatic_share_optimization_performed": False,
        "award_recommendation_created": False,
        "external_data_used": False,
        "tms_erp_writeback_performed": False,
        "human_approval_required": True,
    }


def compare_allocation_scenarios(
    scenarios: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Summarize already-evaluated scenarios without selecting a winner."""
    if (
        not isinstance(scenarios, Sequence)
        or isinstance(scenarios, (str, bytes))
        or not scenarios
    ):
        raise ValueError("At least one evaluated scenario is required.")

    rows: list[dict[str, Any]] = []
    for index, scenario in enumerate(scenarios, start=1):
        required = (
            "scenario_name",
            "status",
            "effective_annual_trip_demand",
            "portfolio_annual_freight_cost_inr",
            "weighted_freight_cost_inr_per_trip",
        )
        missing = [field for field in required if field not in scenario]
        if missing:
            raise ValueError(
                f"Scenario {index} missing required evaluated fields: " + ", ".join(missing)
            )
        rows.append(
            {
                "scenario_name": scenario["scenario_name"],
                "status": scenario["status"],
                "effective_annual_trip_demand": scenario["effective_annual_trip_demand"],
                "portfolio_annual_freight_cost_inr": scenario[
                    "portfolio_annual_freight_cost_inr"
                ],
                "weighted_freight_cost_inr_per_trip": scenario[
                    "weighted_freight_cost_inr_per_trip"
                ],
            }
        )

    return {
        "contract_version": ALLOCATION_SCENARIO_VERSION,
        "scenarios": rows,
        "winner_selected": False,
        "recommendation_created": False,
        "human_approval_required": True,
    }
