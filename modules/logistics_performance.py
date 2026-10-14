"""Governed LOGISTICS-2 carrier performance and risk evaluation.

The module evaluates explicit FTL carrier performance evidence against explicit
buyer-defined service thresholds. It does not apply hidden weights, create a
composite carrier score, rank carriers, optimize allocations, or recommend an
award.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

from modules.logistics_engine import (
    CATEGORY_NAME,
    ENGINE_STATUS,
    EVIDENCE_STATUSES,
    FIRST_COMMODITY,
)

CARRIER_EVALUATION_VERSION = "LOGISTICS-2"

PERFORMANCE_POLICY_CONTRACT = {
    "contract_version": CARRIER_EVALUATION_VERSION,
    "required_policy_fields": (
        "maximum_transit_time_days",
        "minimum_otif_pct",
        "maximum_damage_claim_rate_pct",
        "require_capacity_confirmation",
        "accepted_compliance_statuses",
    ),
    "required_evidence_fields": (
        "capacity_confirmed",
        "transit_time_days",
        "otif_pct",
        "damage_claim_rate_pct",
        "compliance_status",
        "evidence_status",
        "source_label",
    ),
    "evaluation_dimensions": (
        "capacity confirmation",
        "transit time",
        "OTIF",
        "damage / claims",
        "compliance evidence",
        "evidence quality",
    ),
    "governance_note": (
        "Thresholds are buyer-supplied policy inputs. LOGISTICS-2 does not invent "
        "thresholds, weights, carrier scores, ranks, allocations, routes, or awards."
    ),
}


def _finite_number(name: str, value: Any, *, non_negative: bool = False) -> float:
    """Return a finite governed numeric input or fail closed."""
    try:
        numeric = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric.") from exc
    if not math.isfinite(numeric):
        raise ValueError(f"{name} must be finite.")
    if non_negative and numeric < 0:
        raise ValueError(f"{name} must be zero or greater.")
    return numeric


def _percentage(name: str, value: Any) -> float:
    numeric = _finite_number(name, value, non_negative=True)
    if numeric > 100:
        raise ValueError(f"{name} must be between zero and 100.")
    return numeric


def _validate_policy(policy: Mapping[str, Any]) -> dict[str, Any]:
    missing = [
        field
        for field in PERFORMANCE_POLICY_CONTRACT["required_policy_fields"]
        if field not in policy or policy.get(field) is None
    ]
    if missing:
        raise ValueError("Missing buyer policy fields: " + ", ".join(missing))

    require_capacity = policy["require_capacity_confirmation"]
    if not isinstance(require_capacity, bool):
        raise ValueError("require_capacity_confirmation must be a boolean.")

    accepted = policy["accepted_compliance_statuses"]
    if isinstance(accepted, str) or not isinstance(accepted, Sequence):
        raise ValueError("accepted_compliance_statuses must be a non-empty sequence.")
    accepted_clean = tuple(str(item).strip() for item in accepted if str(item).strip())
    if not accepted_clean:
        raise ValueError("accepted_compliance_statuses must be a non-empty sequence.")

    return {
        "maximum_transit_time_days": _finite_number(
            "Maximum transit time days",
            policy["maximum_transit_time_days"],
            non_negative=True,
        ),
        "minimum_otif_pct": _percentage("Minimum OTIF percent", policy["minimum_otif_pct"]),
        "maximum_damage_claim_rate_pct": _percentage(
            "Maximum damage claim rate percent",
            policy["maximum_damage_claim_rate_pct"],
        ),
        "require_capacity_confirmation": require_capacity,
        "accepted_compliance_statuses": accepted_clean,
    }


def _validate_evidence(evidence: Mapping[str, Any]) -> dict[str, Any]:
    missing = [
        field
        for field in PERFORMANCE_POLICY_CONTRACT["required_evidence_fields"]
        if field not in evidence or evidence.get(field) is None
    ]
    if missing:
        raise ValueError("Missing carrier performance evidence fields: " + ", ".join(missing))

    capacity_confirmed = evidence["capacity_confirmed"]
    if not isinstance(capacity_confirmed, bool):
        raise ValueError("capacity_confirmed must be a boolean.")

    evidence_status = str(evidence["evidence_status"]).strip()
    if evidence_status not in EVIDENCE_STATUSES:
        raise ValueError(f"Unsupported evidence status: {evidence_status}")

    source_label = str(evidence["source_label"]).strip()
    if not source_label:
        raise ValueError("Source label is required for carrier performance provenance.")

    compliance_status = str(evidence["compliance_status"]).strip()
    if not compliance_status:
        raise ValueError("compliance_status must not be blank.")

    return {
        "capacity_confirmed": capacity_confirmed,
        "transit_time_days": _finite_number(
            "Transit time days", evidence["transit_time_days"], non_negative=True
        ),
        "otif_pct": _percentage("OTIF percent", evidence["otif_pct"]),
        "damage_claim_rate_pct": _percentage(
            "Damage claim rate percent", evidence["damage_claim_rate_pct"]
        ),
        "compliance_status": compliance_status,
        "evidence_status": evidence_status,
        "source_label": source_label,
    }


def get_carrier_evaluation_profile() -> dict[str, Any]:
    """Return the bounded LOGISTICS-2 carrier-evaluation contract."""
    return {
        "category": CATEGORY_NAME,
        "service": FIRST_COMMODITY,
        "engine_status": ENGINE_STATUS,
        "contract_version": CARRIER_EVALUATION_VERSION,
        "contract": dict(PERFORMANCE_POLICY_CONTRACT),
        "composite_score_enabled": False,
        "carrier_ranking_enabled": False,
        "allocation_enabled": False,
        "route_optimization_enabled": False,
        "award_recommendation_enabled": False,
        "human_approval_required": True,
    }


def evaluate_carrier_performance(
    *,
    carrier_id: str,
    carrier_name: str,
    performance_evidence: Mapping[str, Any],
    buyer_policy: Mapping[str, Any],
) -> dict[str, Any]:
    """Evaluate one carrier against explicit buyer service thresholds."""
    carrier_id_clean = str(carrier_id or "").strip()
    carrier_name_clean = str(carrier_name or "").strip()
    if not carrier_id_clean:
        raise ValueError("carrier_id is required.")
    if not carrier_name_clean:
        raise ValueError("carrier_name is required.")

    policy = _validate_policy(buyer_policy)
    evidence = _validate_evidence(performance_evidence)

    capacity_pass = (
        not policy["require_capacity_confirmation"] or evidence["capacity_confirmed"]
    )
    transit_pass = (
        evidence["transit_time_days"] <= policy["maximum_transit_time_days"]
    )
    otif_pass = evidence["otif_pct"] >= policy["minimum_otif_pct"]
    damage_pass = (
        evidence["damage_claim_rate_pct"]
        <= policy["maximum_damage_claim_rate_pct"]
    )
    compliance_pass = (
        evidence["compliance_status"] in policy["accepted_compliance_statuses"]
    )
    evidence_verified = evidence["evidence_status"] == "Verified by Human Review"

    criteria = (
        {
            "criterion": "capacity confirmation",
            "status": "PASS" if capacity_pass else "FAIL",
            "actual": evidence["capacity_confirmed"],
            "policy": policy["require_capacity_confirmation"],
            "risk_dimension": "carrier capacity availability risk",
        },
        {
            "criterion": "transit time",
            "status": "PASS" if transit_pass else "FAIL",
            "actual": evidence["transit_time_days"],
            "policy": policy["maximum_transit_time_days"],
            "risk_dimension": "transit-time and service reliability risk",
        },
        {
            "criterion": "OTIF",
            "status": "PASS" if otif_pass else "FAIL",
            "actual": evidence["otif_pct"],
            "policy": policy["minimum_otif_pct"],
            "risk_dimension": "transit-time and service reliability risk",
        },
        {
            "criterion": "damage / claims",
            "status": "PASS" if damage_pass else "FAIL",
            "actual": evidence["damage_claim_rate_pct"],
            "policy": policy["maximum_damage_claim_rate_pct"],
            "risk_dimension": "damage and claims risk",
        },
        {
            "criterion": "compliance evidence",
            "status": "PASS" if compliance_pass else "FAIL",
            "actual": evidence["compliance_status"],
            "policy": policy["accepted_compliance_statuses"],
            "risk_dimension": "compliance, safety, and evidence-quality risk",
        },
        {
            "criterion": "evidence quality",
            "status": "PASS" if evidence_verified else "REVIEW",
            "actual": evidence["evidence_status"],
            "policy": "Verified by Human Review",
            "risk_dimension": "compliance, safety, and evidence-quality risk",
        },
    )

    failed = [item for item in criteria if item["status"] == "FAIL"]
    review = [item for item in criteria if item["status"] == "REVIEW"]

    if failed:
        overall_status = "DOES_NOT_MEET_BUYER_POLICY"
    elif review:
        overall_status = "MEETS_POLICY_WITH_UNVERIFIED_EVIDENCE"
    else:
        overall_status = "MEETS_BUYER_POLICY_FOR_HUMAN_REVIEW"

    risk_flags = []
    for item in (*failed, *review):
        dimension = str(item["risk_dimension"])
        if dimension not in risk_flags:
            risk_flags.append(dimension)

    return {
        "contract_version": CARRIER_EVALUATION_VERSION,
        "category": CATEGORY_NAME,
        "service": FIRST_COMMODITY,
        "carrier_id": carrier_id_clean,
        "carrier_name": carrier_name_clean,
        "overall_status": overall_status,
        "criteria": list(criteria),
        "policy_breach_count": len(failed),
        "review_flag_count": len(review),
        "risk_flags": risk_flags,
        "evidence_status": evidence["evidence_status"],
        "source_label": evidence["source_label"],
        "buyer_policy": policy,
        "composite_score": None,
        "rank": None,
        "ranking_performed": False,
        "allocation_performed": False,
        "route_optimization_performed": False,
        "award_recommendation_created": False,
        "external_data_used": False,
        "human_approval_required": True,
    }
