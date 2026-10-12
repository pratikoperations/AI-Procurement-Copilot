"""Governed MRO / Industrial Supplies foundation contracts.

MRO-0 defines category identity, technical compatibility and supplier/evidence
contracts only. It intentionally does not provide should-cost, scoring,
scenario, allocation or autonomous decision logic.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from modules.commodity_library import get_commodities, get_commodity_profile

CATEGORY_NAME = "MRO / Industrial Supplies"
ENGINE_STATUS = "Foundation Preview"
FOUNDATION_VERSION = "MRO-0"
FIRST_COMMODITY = "Industrial Bearings"

SOURCE_STATUSES = (
    "OEM",
    "Authorized Distributor",
    "Approved Equivalent",
)

EVIDENCE_STATUSES = (
    "Synthetic Demonstration",
    "Supplied — Unverified",
    "Verified by Human Review",
)

SUBSTITUTION_APPROVAL_STATUSES = (
    "Not Applicable",
    "Human Review Required",
    "Human Approved",
    "Rejected",
)

TECHNICAL_CONTRACT = {
    "required_identity_fields": (
        "manufacturer",
        "manufacturer_part_number",
    ),
    "required_compatibility_fields": (
        "bearing_type",
        "bore_diameter_mm",
        "outside_diameter_mm",
        "width_mm",
        "seal_or_shield",
        "clearance_class",
    ),
    "compatibility_rule": (
        "Fail closed: every required technical field must be supplied and match the governed requirement. "
        "Missing or conflicting evidence is not compatible."
    ),
}

COMMERCIAL_CONTRACT = {
    "required_fields": (
        "quote_currency",
        "unit_price",
        "unit",
        "minimum_order_quantity",
        "lead_time_days",
        "payment_terms",
        "quote_validity_date",
    ),
    "comparison_note": (
        "MRO-0 records commercial evidence only. It does not calculate an MRO should-cost, "
        "supplier score or award recommendation."
    ),
}

EVIDENCE_CONTRACT = {
    "required_fields": (
        "evidence_id",
        "evidence_type",
        "evidence_status",
        "source_label",
        "manufacturer",
        "manufacturer_part_number",
    ),
    "allowed_statuses": EVIDENCE_STATUSES,
    "governance_note": (
        "Evidence provenance is preserved. Synthetic demonstration evidence must never be presented "
        "as manufacturer certification or live supplier verification."
    ),
}

SUPPLIER_DATA_CONTRACT = {
    "required_fields": (
        "supplier_id",
        "supplier_name",
        "manufacturer",
        "manufacturer_part_number",
        "source_status",
        "substitution_approval_status",
        "technical_evidence",
        "commercial_evidence",
    ),
    "source_statuses": SOURCE_STATUSES,
    "human_approval_required": True,
}

RISK_DIMENSIONS = (
    "counterfeit and authenticity risk",
    "technical mismatch and substitution risk",
    "manufacturer / channel authorization risk",
    "obsolescence and lifecycle risk",
    "availability and stockout risk",
    "lead-time continuity risk",
    "quality and traceability risk",
    "single-source concentration risk",
)

SYNTHETIC_BEARING_SUPPLIERS = (
    {
        "supplier_id": "MRO-SYN-001",
        "supplier_name": "Synthetic Bearing Supply A",
        "manufacturer": "DemoBearing Co.",
        "manufacturer_part_number": "DB-6205-2RS-C3",
        "source_status": "Authorized Distributor",
        "substitution_approval_status": "Not Applicable",
        "technical_evidence": {
            "bearing_type": "Deep Groove Ball Bearing",
            "bore_diameter_mm": 25,
            "outside_diameter_mm": 52,
            "width_mm": 15,
            "seal_or_shield": "2RS",
            "clearance_class": "C3",
        },
        "commercial_evidence": {
            "quote_currency": "USD",
            "unit_price": 8.40,
            "unit": "piece",
            "minimum_order_quantity": 10,
            "lead_time_days": 14,
            "payment_terms": "30 days",
            "quote_validity_date": "Synthetic demonstration only",
        },
        "evidence": (
            {
                "evidence_id": "MRO-E-SYN-001",
                "evidence_type": "Synthetic distributor authorization record",
                "evidence_status": "Synthetic Demonstration",
                "source_label": "Controlled synthetic MRO-0 demonstration evidence",
                "manufacturer": "DemoBearing Co.",
                "manufacturer_part_number": "DB-6205-2RS-C3",
            },
        ),
    },
    {
        "supplier_id": "MRO-SYN-002",
        "supplier_name": "Synthetic Industrial Supply B",
        "manufacturer": "EquivalentBearing Labs",
        "manufacturer_part_number": "EB-6205-2RS-C3",
        "source_status": "Approved Equivalent",
        "substitution_approval_status": "Human Review Required",
        "technical_evidence": {
            "bearing_type": "Deep Groove Ball Bearing",
            "bore_diameter_mm": 25,
            "outside_diameter_mm": 52,
            "width_mm": 15,
            "seal_or_shield": "2RS",
            "clearance_class": "C3",
        },
        "commercial_evidence": {
            "quote_currency": "USD",
            "unit_price": 7.65,
            "unit": "piece",
            "minimum_order_quantity": 10,
            "lead_time_days": 21,
            "payment_terms": "30 days",
            "quote_validity_date": "Synthetic demonstration only",
        },
        "evidence": (
            {
                "evidence_id": "MRO-E-SYN-002",
                "evidence_type": "Synthetic equivalent-part comparison record",
                "evidence_status": "Synthetic Demonstration",
                "source_label": "Controlled synthetic MRO-0 demonstration evidence",
                "manufacturer": "EquivalentBearing Labs",
                "manufacturer_part_number": "EB-6205-2RS-C3",
            },
        ),
    },
)


def get_engine_profile(commodity: str | None = None) -> dict[str, Any]:
    """Return the governed MRO foundation profile without inherited category weights."""
    commodities = get_commodities(CATEGORY_NAME)
    selected = commodity if commodity in commodities else FIRST_COMMODITY
    profile = get_commodity_profile(CATEGORY_NAME, selected)
    return {
        "category": CATEGORY_NAME,
        "category_name": CATEGORY_NAME,
        "engine_status": ENGINE_STATUS,
        "selected_commodity": selected,
        "commodity_group": profile.get("family", "MRO / Industrial Supplies"),
        "commodities": commodities,
        "cost_model": "No MRO should-cost model in MRO-0",
        "risk_model": "Qualitative governed MRO risk dimensions; no unsupported numerical weights",
        "unit": profile.get("unit", "piece"),
        "units": [profile.get("unit", "piece")],
        "currency": "USD",
        "primary_cost_drivers": profile.get("primary_cost_drivers", []),
        "risk_signals": list(RISK_DIMENSIONS),
        "default_weightings": {},
        "default_assumptions": {},
        "allocation_model": "Not enabled in MRO-0",
        "technical_contract": deepcopy(TECHNICAL_CONTRACT),
        "commercial_contract": deepcopy(COMMERCIAL_CONTRACT),
        "evidence_contract": deepcopy(EVIDENCE_CONTRACT),
        "supplier_data_contract": deepcopy(SUPPLIER_DATA_CONTRACT),
        "implementation_note": (
            "Foundation Preview only. Technical compatibility is fail-closed; substitution and supplier "
            "selection require human procurement approval. No MRO should-cost, scoring, scenario or "
            "percentage-allocation engine is active."
        ),
    }


def evaluate_technical_compatibility(
    requirement: Mapping[str, Any],
    offer: Mapping[str, Any],
    *,
    source_status: str,
    substitution_approval_status: str = "Not Applicable",
) -> dict[str, Any]:
    """Evaluate MRO technical compatibility using fail-closed deterministic rules."""
    if source_status not in SOURCE_STATUSES:
        return {
            "compatible": False,
            "status": "INVALID_SOURCE_STATUS",
            "reasons": [f"Unsupported source status: {source_status}"],
            "human_approval_required": True,
        }

    required_fields = tuple(TECHNICAL_CONTRACT["required_compatibility_fields"])
    missing = [
        field
        for field in required_fields
        if requirement.get(field) is None or offer.get(field) is None
    ]
    if missing:
        return {
            "compatible": False,
            "status": "INSUFFICIENT_EVIDENCE",
            "reasons": [f"Missing governed technical evidence: {field}" for field in missing],
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
            "reasons": [f"Technical mismatch: {field}" for field in mismatches],
            "human_approval_required": True,
        }

    if source_status == "Approved Equivalent" and substitution_approval_status != "Human Approved":
        return {
            "compatible": False,
            "status": "HUMAN_APPROVAL_REQUIRED",
            "reasons": ["Approved-equivalent substitution requires explicit human approval."],
            "human_approval_required": True,
        }

    return {
        "compatible": True,
        "status": "COMPATIBLE_FOR_HUMAN_REVIEW",
        "reasons": [],
        "human_approval_required": True,
    }


def get_synthetic_demo_suppliers() -> list[dict[str, Any]]:
    """Return isolated synthetic MRO-0 supplier examples."""
    return [deepcopy(item) for item in SYNTHETIC_BEARING_SUPPLIERS]
