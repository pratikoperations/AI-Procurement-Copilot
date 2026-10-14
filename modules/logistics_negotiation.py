"""Governed LOGISTICS-4 negotiation intelligence and decision presentation.

LOGISTICS-4 turns explicit carrier commercial inputs and explicit buyer negotiation
positions into deterministic, reviewable negotiation deltas. It does not invent
targets, negotiate autonomously, commit commercial terms, or make an award.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from modules.logistics_engine import CATEGORY_NAME, ENGINE_STATUS, FIRST_COMMODITY

NEGOTIATION_VERSION = "LOGISTICS-4"

NEGOTIATION_CONTRACT = {
    "contract_version": NEGOTIATION_VERSION,
    "required_carrier_fields": (
        "carrier_id",
        "carrier_name",
        "current_landed_freight_inr_per_trip",
        "annual_allocated_trips",
        "source_label",
    ),
    "required_position_fields": (
        "target_freight_inr_per_trip",
        "commercial_ceiling_inr_per_trip",
        "target_payment_terms_days",
        "target_detention_free_hours",
        "target_service_commitment",
    ),
    "governance_note": (
        "Negotiation targets are explicit buyer inputs. LOGISTICS-4 calculates "
        "commercial deltas and presents negotiation priorities without inventing "
        "targets, committing terms, selecting carriers, or creating an award."
    ),
}


def _finite_number(name: str, value: Any, *, non_negative: bool = False) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric.") from exc
    if not math.isfinite(numeric):
        raise ValueError(f"{name} must be finite.")
    if non_negative and numeric < 0:
        raise ValueError(f"{name} must be zero or greater.")
    return numeric


def get_negotiation_profile() -> dict[str, Any]:
    """Return the bounded LOGISTICS-4 negotiation contract."""
    return {
        "category": CATEGORY_NAME,
        "service": FIRST_COMMODITY,
        "engine_status": ENGINE_STATUS,
        "contract_version": NEGOTIATION_VERSION,
        "contract": dict(NEGOTIATION_CONTRACT),
        "autonomous_negotiation_enabled": False,
        "commercial_commitment_enabled": False,
        "carrier_selection_enabled": False,
        "award_recommendation_enabled": False,
        "human_approval_required": True,
    }


def build_carrier_negotiation_brief(
    *,
    carrier: Mapping[str, Any],
    buyer_position: Mapping[str, Any],
) -> dict[str, Any]:
    """Build deterministic negotiation deltas from explicit buyer positions."""
    missing_carrier = [
        field
        for field in NEGOTIATION_CONTRACT["required_carrier_fields"]
        if field not in carrier or carrier.get(field) is None
    ]
    if missing_carrier:
        raise ValueError("Missing carrier negotiation fields: " + ", ".join(missing_carrier))

    missing_position = [
        field
        for field in NEGOTIATION_CONTRACT["required_position_fields"]
        if field not in buyer_position or buyer_position.get(field) is None
    ]
    if missing_position:
        raise ValueError("Missing buyer negotiation position fields: " + ", ".join(missing_position))

    carrier_id = str(carrier["carrier_id"]).strip()
    carrier_name = str(carrier["carrier_name"]).strip()
    source_label = str(carrier["source_label"]).strip()
    if not carrier_id:
        raise ValueError("carrier_id is required.")
    if not carrier_name:
        raise ValueError("carrier_name is required.")
    if not source_label:
        raise ValueError("source_label is required.")

    current = _finite_number(
        "Current landed freight INR/trip",
        carrier["current_landed_freight_inr_per_trip"],
        non_negative=True,
    )
    annual_trips = _finite_number(
        "Annual allocated trips",
        carrier["annual_allocated_trips"],
        non_negative=True,
    )
    target = _finite_number(
        "Target freight INR/trip",
        buyer_position["target_freight_inr_per_trip"],
        non_negative=True,
    )
    ceiling = _finite_number(
        "Commercial ceiling INR/trip",
        buyer_position["commercial_ceiling_inr_per_trip"],
        non_negative=True,
    )
    payment_days = _finite_number(
        "Target payment terms days",
        buyer_position["target_payment_terms_days"],
        non_negative=True,
    )
    detention_hours = _finite_number(
        "Target detention free hours",
        buyer_position["target_detention_free_hours"],
        non_negative=True,
    )
    service_commitment = str(buyer_position["target_service_commitment"]).strip()
    if not service_commitment:
        raise ValueError("target_service_commitment is required.")
    if target > ceiling:
        raise ValueError("Target freight INR/trip must not exceed the commercial ceiling.")

    target_saving_per_trip = max(current - target, 0.0)
    ceiling_saving_per_trip = max(current - ceiling, 0.0)
    annual_target_saving = target_saving_per_trip * annual_trips
    annual_ceiling_saving = ceiling_saving_per_trip * annual_trips

    if current > ceiling:
        price_position = "ABOVE_BUYER_CEILING"
    elif current > target:
        price_position = "WITHIN_NEGOTIATION_RANGE"
    else:
        price_position = "AT_OR_BELOW_TARGET"

    priorities = []
    if current > target:
        priorities.append("Freight rate")
    if payment_days > 0:
        priorities.append("Payment terms")
    if detention_hours > 0:
        priorities.append("Detention terms")
    priorities.append("Service commitment")

    return {
        "contract_version": NEGOTIATION_VERSION,
        "category": CATEGORY_NAME,
        "service": FIRST_COMMODITY,
        "carrier_id": carrier_id,
        "carrier_name": carrier_name,
        "source_label": source_label,
        "current_landed_freight_inr_per_trip": current,
        "annual_allocated_trips": annual_trips,
        "target_freight_inr_per_trip": target,
        "commercial_ceiling_inr_per_trip": ceiling,
        "price_position": price_position,
        "target_saving_inr_per_trip": target_saving_per_trip,
        "annual_target_saving_inr": annual_target_saving,
        "annual_ceiling_saving_inr": annual_ceiling_saving,
        "target_payment_terms_days": payment_days,
        "target_detention_free_hours": detention_hours,
        "target_service_commitment": service_commitment,
        "negotiation_priorities": priorities,
        "autonomous_negotiation_performed": False,
        "commercial_commitment_created": False,
        "award_recommendation_created": False,
        "human_approval_required": True,
    }


def build_logistics_decision_summary(
    *,
    scenario_result: Mapping[str, Any],
    negotiation_briefs: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Present a human-readable Logistics decision-support summary."""
    required_scenario = (
        "scenario_name",
        "status",
        "effective_annual_trip_demand",
        "portfolio_annual_freight_cost_inr",
        "weighted_freight_cost_inr_per_trip",
    )
    missing = [field for field in required_scenario if field not in scenario_result]
    if missing:
        raise ValueError("Missing scenario result fields: " + ", ".join(missing))
    if isinstance(negotiation_briefs, (str, bytes)) or not isinstance(
        negotiation_briefs, Sequence
    ):
        raise ValueError("negotiation_briefs must be a sequence.")

    total_target_saving = 0.0
    carrier_rows = []
    for index, brief in enumerate(negotiation_briefs, start=1):
        required = (
            "carrier_id",
            "carrier_name",
            "price_position",
            "annual_target_saving_inr",
            "negotiation_priorities",
        )
        brief_missing = [field for field in required if field not in brief]
        if brief_missing:
            raise ValueError(
                f"Negotiation brief {index} missing fields: " + ", ".join(brief_missing)
            )
        saving = _finite_number(
            f"Negotiation brief {index} annual target saving INR",
            brief["annual_target_saving_inr"],
            non_negative=True,
        )
        total_target_saving += saving
        carrier_rows.append(
            {
                "carrier_id": brief["carrier_id"],
                "carrier_name": brief["carrier_name"],
                "price_position": brief["price_position"],
                "annual_target_saving_inr": saving,
                "negotiation_priorities": list(brief["negotiation_priorities"]),
            }
        )

    return {
        "contract_version": NEGOTIATION_VERSION,
        "scenario_name": scenario_result["scenario_name"],
        "scenario_status": scenario_result["status"],
        "effective_annual_trip_demand": scenario_result["effective_annual_trip_demand"],
        "portfolio_annual_freight_cost_inr": scenario_result[
            "portfolio_annual_freight_cost_inr"
        ],
        "weighted_freight_cost_inr_per_trip": scenario_result[
            "weighted_freight_cost_inr_per_trip"
        ],
        "carrier_negotiation_summary": carrier_rows,
        "potential_annual_target_saving_inr": total_target_saving,
        "decision_message": (
            "Review carrier feasibility, evidence quality, allocation scenario, and explicit "
            "negotiation positions together before any commercial commitment."
        ),
        "scenario_winner_selected": False,
        "carrier_award_selected": False,
        "commercial_commitment_created": False,
        "human_approval_required": True,
    }
