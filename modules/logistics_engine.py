"""Governed Logistics & Freight foundation contracts.

LOGISTICS-0 defines service identity, lane compatibility, carrier/evidence
contracts, and synthetic demonstration records only. It intentionally does not
provide freight-cost calculation, carrier scoring, scenario, allocation,
optimization, negotiation, or autonomous award logic.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from modules.commodity_library import get_commodities, get_commodity_profile

CATEGORY_NAME = "Logistics & Freight"
ENGINE_STATUS = "Foundation Preview"
FOUNDATION_VERSION = "LOGISTICS-0"
FREIGHT_NORMALIZATION_VERSION = "LOGISTICS-1"
FIRST_COMMODITY = "Domestic Road Transportation — FTL"

CARRIER_STATUSES = (
    "Contracted Carrier",
    "Approved Carrier",
    "Spot / Unverified Carrier",
)

EVIDENCE_STATUSES = (
    "Synthetic Demonstration",
    "Supplied — Unverified",
    "Verified by Human Review",
)

CARRIER_APPROVAL_STATUSES = (
    "Not Applicable",
    "Human Review Required",
    "Human Approved",
    "Rejected",
)

LANE_SERVICE_CONTRACT = {
    "required_identity_fields": (
        "origin_location",
        "destination_location",
        "transport_mode",
        "service_type",
    ),
    "required_compatibility_fields": (
        "origin_location",
        "destination_location",
        "transport_mode",
        "service_type",
        "vehicle_type",
        "minimum_payload_capacity_tonnes",
    ),
    "compatibility_rule": (
        "Fail closed: every required lane/service field must be supplied and match the governed requirement. "
        "Missing or conflicting service evidence is not compatible."
    ),
}

COMMERCIAL_CONTRACT = {
    "required_fields": (
        "quote_currency",
        "base_freight_rate",
        "rate_basis",
        "fuel_surcharge_basis",
        "toll_treatment",
        "detention_terms",
        "loading_unloading_terms",
        "payment_terms",
        "quote_validity_date",
    ),
    "comparison_note": (
        "LOGISTICS-0 records commercial evidence only. It does not normalize freight cost, calculate "
        "fuel/toll adjustments, score carriers, optimize routes, or produce an award recommendation."
    ),
}

PERFORMANCE_CONTRACT = {
    "required_fields": (
        "service_capacity_status",
        "transit_time_days",
        "otif_pct",
        "damage_claim_rate_pct",
    ),
    "governance_note": (
        "LOGISTICS-0 records supplied or synthetic performance evidence without applying score weights, "
        "performance thresholds, or carrier-ranking logic."
    ),
}

EVIDENCE_CONTRACT = {
    "required_fields": (
        "evidence_id",
        "evidence_type",
        "evidence_status",
        "source_label",
        "carrier_name",
        "origin_location",
        "destination_location",
    ),
    "allowed_statuses": EVIDENCE_STATUSES,
    "governance_note": (
        "Evidence provenance is preserved. Synthetic demonstration evidence must never be presented as "
        "live carrier certification, route telemetry, fuel-market data, or external verification."
    ),
}

CARRIER_DATA_CONTRACT = {
    "required_fields": (
        "carrier_id",
        "carrier_name",
        "carrier_status",
        "carrier_approval_status",
        "lane_service_evidence",
        "commercial_evidence",
        "performance_evidence",
    ),
    "carrier_statuses": CARRIER_STATUSES,
    "human_approval_required": True,
}

FREIGHT_NORMALIZATION_CONTRACT = {
    "contract_version": FREIGHT_NORMALIZATION_VERSION,
    "supported_quote_currencies": ("INR",),
    "supported_rate_bases": ("Per Trip", "Per Tonne", "Per Tonne-Km"),
    "fuel_surcharge_treatments": (
        "Included",
        "Fixed Amount Per Trip",
        "Percent of Base Freight",
    ),
    "toll_treatments": (
        "Included",
        "Fixed Amount Per Trip",
    ),
    "required_inputs": (
        "base_freight_rate",
        "rate_basis",
        "payload_tonnes",
        "lane_distance_km",
        "quote_currency",
        "fuel_surcharge_treatment",
        "fuel_surcharge_value",
        "toll_treatment",
        "toll_amount",
        "detention_amount",
        "loading_unloading_amount",
        "other_accessorial_amount",
        "evidence_status",
        "source_label",
    ),
    "governance_note": (
        "LOGISTICS-1 normalizes only explicitly supplied commercial inputs. It does not infer lane distance, "
        "fuel price, tolls, detention, accessorials, market benchmarks, carrier scores, allocations, routes, "
        "or award recommendations."
    ),
}

RISK_DIMENSIONS = (
    "carrier capacity availability risk",
    "lane coverage and continuity risk",
    "transit-time and service reliability risk",
    "damage and claims risk",
    "detention and turnaround-time risk",
    "fuel and toll commercial volatility",
    "carrier concentration risk",
    "compliance, safety, and evidence-quality risk",
)

SYNTHETIC_FTL_CARRIERS = (
    {
        "carrier_id": "LOG-SYN-001",
        "carrier_name": "Synthetic Road Carrier A",
        "carrier_status": "Approved Carrier",
        "carrier_approval_status": "Not Applicable",
        "lane_service_evidence": {
            "origin_location": "Pune, Maharashtra",
            "destination_location": "Navi Mumbai, Maharashtra",
            "transport_mode": "Road",
            "service_type": "Full Truck Load",
            "vehicle_type": "Closed Body Truck",
            "minimum_payload_capacity_tonnes": 16,
        },
        "commercial_evidence": {
            "quote_currency": "INR",
            "base_freight_rate": 24500,
            "rate_basis": "Per Trip",
            "fuel_surcharge_basis": "Included in synthetic base rate",
            "toll_treatment": "Included in synthetic base rate",
            "detention_terms": "Synthetic demonstration terms",
            "loading_unloading_terms": "Synthetic demonstration terms",
            "payment_terms": "30 days",
            "quote_validity_date": "Synthetic demonstration only",
        },
        "performance_evidence": {
            "service_capacity_status": "Synthetic capacity available",
            "transit_time_days": 1,
            "otif_pct": 96.0,
            "damage_claim_rate_pct": 0.4,
        },
        "evidence": (
            {
                "evidence_id": "LOG-E-SYN-001",
                "evidence_type": "Synthetic carrier lane capability record",
                "evidence_status": "Synthetic Demonstration",
                "source_label": "Controlled synthetic LOGISTICS-0 demonstration evidence",
                "carrier_name": "Synthetic Road Carrier A",
                "origin_location": "Pune, Maharashtra",
                "destination_location": "Navi Mumbai, Maharashtra",
            },
        ),
    },
    {
        "carrier_id": "LOG-SYN-002",
        "carrier_name": "Synthetic Road Carrier B",
        "carrier_status": "Spot / Unverified Carrier",
        "carrier_approval_status": "Human Review Required",
        "lane_service_evidence": {
            "origin_location": "Pune, Maharashtra",
            "destination_location": "Navi Mumbai, Maharashtra",
            "transport_mode": "Road",
            "service_type": "Full Truck Load",
            "vehicle_type": "Closed Body Truck",
            "minimum_payload_capacity_tonnes": 16,
        },
        "commercial_evidence": {
            "quote_currency": "INR",
            "base_freight_rate": 23100,
            "rate_basis": "Per Trip",
            "fuel_surcharge_basis": "Synthetic separate surcharge reference",
            "toll_treatment": "Synthetic pass-through reference",
            "detention_terms": "Synthetic demonstration terms",
            "loading_unloading_terms": "Synthetic demonstration terms",
            "payment_terms": "30 days",
            "quote_validity_date": "Synthetic demonstration only",
        },
        "performance_evidence": {
            "service_capacity_status": "Synthetic capacity not independently verified",
            "transit_time_days": 1,
            "otif_pct": 93.0,
            "damage_claim_rate_pct": 0.8,
        },
        "evidence": (
            {
                "evidence_id": "LOG-E-SYN-002",
                "evidence_type": "Synthetic spot-carrier capability record",
                "evidence_status": "Synthetic Demonstration",
                "source_label": "Controlled synthetic LOGISTICS-0 demonstration evidence",
                "carrier_name": "Synthetic Road Carrier B",
                "origin_location": "Pune, Maharashtra",
                "destination_location": "Navi Mumbai, Maharashtra",
            },
        ),
    },
)


def get_engine_profile(commodity: str | None = None) -> dict[str, Any]:
    """Return the governed Logistics foundation profile without inherited weights."""
    commodities = get_commodities(CATEGORY_NAME)
    selected = commodity if commodity in commodities else FIRST_COMMODITY
    profile = get_commodity_profile(CATEGORY_NAME, selected)
    unit = profile.get("unit", "trip")
    return {
        "category": CATEGORY_NAME,
        "category_name": CATEGORY_NAME,
        "engine_status": ENGINE_STATUS,
        "selected_commodity": selected,
        "commodity_group": profile.get("family", "Logistics & Freight"),
        "commodities": commodities,
        "cost_model": "No freight-cost calculation model in LOGISTICS-0",
        "risk_model": "Qualitative governed logistics risk dimensions; no unsupported numerical weights",
        "unit": unit,
        "units": [unit],
        "currency": "INR",
        "primary_cost_drivers": profile.get("primary_cost_drivers", []),
        "risk_signals": list(RISK_DIMENSIONS),
        "default_weightings": {},
        "default_assumptions": {},
        "allocation_model": "Not enabled in LOGISTICS-0",
        "lane_service_contract": deepcopy(LANE_SERVICE_CONTRACT),
        "commercial_contract": deepcopy(COMMERCIAL_CONTRACT),
        "performance_contract": deepcopy(PERFORMANCE_CONTRACT),
        "evidence_contract": deepcopy(EVIDENCE_CONTRACT),
        "carrier_data_contract": deepcopy(CARRIER_DATA_CONTRACT),
        "implementation_note": (
            "Foundation Preview only. Lane/service compatibility is fail-closed and carrier selection requires "
            "human procurement approval. No freight-cost calculation, carrier scoring, scenario, allocation, "
            "optimization, negotiation, live route/fuel data, or autonomous award engine is active."
        ),
    }


def evaluate_service_compatibility(
    requirement: Mapping[str, Any],
    offer: Mapping[str, Any],
    *,
    carrier_status: str,
    carrier_approval_status: str = "Not Applicable",
) -> dict[str, Any]:
    """Evaluate FTL lane/service compatibility using fail-closed deterministic rules."""
    if carrier_status not in CARRIER_STATUSES:
        return {
            "compatible": False,
            "status": "INVALID_CARRIER_STATUS",
            "reasons": [f"Unsupported carrier status: {carrier_status}"],
            "human_approval_required": True,
        }

    required_fields = tuple(LANE_SERVICE_CONTRACT["required_compatibility_fields"])
    missing = [
        field
        for field in required_fields
        if requirement.get(field) is None or offer.get(field) is None
    ]
    if missing:
        return {
            "compatible": False,
            "status": "INSUFFICIENT_EVIDENCE",
            "reasons": [f"Missing governed lane/service evidence: {field}" for field in missing],
            "human_approval_required": True,
        }

    mismatches = [
        field
        for field in required_fields
        if requirement.get(field) != offer.get(field)
    ]
    if mismatches:
        return {
            "compatible": False,
            "status": "INCOMPATIBLE",
            "reasons": [f"Lane/service mismatch: {field}" for field in mismatches],
            "human_approval_required": True,
        }

    if carrier_status == "Spot / Unverified Carrier" and carrier_approval_status != "Human Approved":
        return {
            "compatible": False,
            "status": "HUMAN_APPROVAL_REQUIRED",
            "reasons": ["Spot / unverified carrier requires explicit human approval."],
            "human_approval_required": True,
        }

    return {
        "compatible": True,
        "status": "COMPATIBLE_FOR_HUMAN_REVIEW",
        "reasons": [],
        "human_approval_required": True,
    }


def get_synthetic_demo_carriers() -> list[dict[str, Any]]:
    """Return isolated synthetic LOGISTICS-0 carrier examples."""
    return [deepcopy(item) for item in SYNTHETIC_FTL_CARRIERS]



def _finite_number(name: str, value: Any, *, positive: bool = False, non_negative: bool = False) -> float:
    """Return a finite governed numeric input or fail closed."""
    import math

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


def get_freight_normalization_profile() -> dict[str, Any]:
    """Return the bounded LOGISTICS-1 freight-normalization contract."""
    return {
        "category": CATEGORY_NAME,
        "service": FIRST_COMMODITY,
        "engine_status": ENGINE_STATUS,
        "contract_version": FREIGHT_NORMALIZATION_VERSION,
        "calculation_currency": "INR",
        "comparison_units": ("INR/trip", "INR/tonne", "INR/tonne-km"),
        "contract": deepcopy(FREIGHT_NORMALIZATION_CONTRACT),
        "carrier_scoring_enabled": False,
        "scenario_engine_enabled": False,
        "allocation_enabled": False,
        "route_optimization_enabled": False,
        "autonomous_award_enabled": False,
        "human_approval_required": True,
    }


def normalize_ftl_freight_quote(
    *,
    base_freight_rate: Any,
    rate_basis: str,
    payload_tonnes: Any,
    lane_distance_km: Any,
    quote_currency: str = "INR",
    fuel_surcharge_treatment: str = "Included",
    fuel_surcharge_value: Any = 0.0,
    toll_treatment: str = "Included",
    toll_amount: Any = 0.0,
    detention_amount: Any = 0.0,
    loading_unloading_amount: Any = 0.0,
    other_accessorial_amount: Any = 0.0,
    evidence_status: str = "Supplied — Unverified",
    source_label: str = "User-supplied commercial evidence",
) -> dict[str, Any]:
    """Normalize an explicitly supplied FTL quote to governed comparable INR units.

    No market data, route distance, fuel rate, toll, detention, or accessorial
    amount is inferred. Carrier ranking, allocation, optimization, negotiation,
    and award decisions remain outside LOGISTICS-1.
    """
    contract = FREIGHT_NORMALIZATION_CONTRACT
    if quote_currency not in contract["supported_quote_currencies"]:
        raise ValueError("LOGISTICS-1 supports INR quotations only; no FX conversion is inferred.")
    if rate_basis not in contract["supported_rate_bases"]:
        raise ValueError(f"Unsupported freight rate basis: {rate_basis}")
    if fuel_surcharge_treatment not in contract["fuel_surcharge_treatments"]:
        raise ValueError(f"Unsupported fuel surcharge treatment: {fuel_surcharge_treatment}")
    if toll_treatment not in contract["toll_treatments"]:
        raise ValueError(f"Unsupported toll treatment: {toll_treatment}")
    if evidence_status not in EVIDENCE_STATUSES:
        raise ValueError(f"Unsupported evidence status: {evidence_status}")
    if not str(source_label or "").strip():
        raise ValueError("Source label is required for freight normalization provenance.")

    base_rate = _finite_number("Base freight rate", base_freight_rate, non_negative=True)
    payload = _finite_number("Payload tonnes", payload_tonnes, positive=True)
    distance = _finite_number("Lane distance km", lane_distance_km, positive=True)
    fuel_value = _finite_number("Fuel surcharge value", fuel_surcharge_value, non_negative=True)
    toll = _finite_number("Toll amount", toll_amount, non_negative=True)
    detention = _finite_number("Detention amount", detention_amount, non_negative=True)
    loading_unloading = _finite_number(
        "Loading/unloading amount", loading_unloading_amount, non_negative=True
    )
    accessorial = _finite_number(
        "Other accessorial amount", other_accessorial_amount, non_negative=True
    )

    if rate_basis == "Per Trip":
        base_per_trip = base_rate
    elif rate_basis == "Per Tonne":
        base_per_trip = base_rate * payload
    else:
        base_per_trip = base_rate * payload * distance

    if fuel_surcharge_treatment == "Included":
        if fuel_value != 0:
            raise ValueError("Included fuel surcharge requires fuel_surcharge_value to be zero.")
        fuel_per_trip = 0.0
    elif fuel_surcharge_treatment == "Fixed Amount Per Trip":
        fuel_per_trip = fuel_value
    else:
        fuel_per_trip = base_per_trip * fuel_value / 100.0

    if toll_treatment == "Included":
        if toll != 0:
            raise ValueError("Included toll treatment requires toll_amount to be zero.")
        toll_per_trip = 0.0
    else:
        toll_per_trip = toll

    components = {
        "Base Freight": base_per_trip,
        "Fuel Surcharge": fuel_per_trip,
        "Toll": toll_per_trip,
        "Detention": detention,
        "Loading / Unloading": loading_unloading,
        "Other Accessorial": accessorial,
    }
    landed_per_trip = sum(components.values())

    return {
        "contract_version": FREIGHT_NORMALIZATION_VERSION,
        "category": CATEGORY_NAME,
        "service": FIRST_COMMODITY,
        "calculation_currency": "INR",
        "quote_currency": quote_currency,
        "rate_basis": rate_basis,
        "base_freight_rate_input": base_rate,
        "payload_tonnes": payload,
        "lane_distance_km": distance,
        "fuel_surcharge_treatment": fuel_surcharge_treatment,
        "fuel_surcharge_value_input": fuel_value,
        "toll_treatment": toll_treatment,
        "components_inr_per_trip": components,
        "normalized_base_freight_inr_per_trip": base_per_trip,
        "landed_freight_inr_per_trip": landed_per_trip,
        "landed_freight_inr_per_tonne": landed_per_trip / payload,
        "landed_freight_inr_per_tonne_km": landed_per_trip / payload / distance,
        "evidence_status": evidence_status,
        "source_label": str(source_label).strip(),
        "external_data_used": False,
        "market_benchmark_inferred": False,
        "carrier_scoring_performed": False,
        "allocation_performed": False,
        "route_optimization_performed": False,
        "award_recommendation_created": False,
        "human_approval_required": True,
        "calculation_trace": {
            "base_normalization": (
                "base rate" if rate_basis == "Per Trip"
                else "base rate × payload tonnes" if rate_basis == "Per Tonne"
                else "base rate × payload tonnes × lane distance km"
            ),
            "landed_freight": (
                "normalized base freight + explicit fuel surcharge + explicit toll + "
                "detention + loading/unloading + other accessorial"
            ),
        },
    }
