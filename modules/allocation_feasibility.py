"""Deterministic feasibility validation for the governed multi-supplier contract."""

from __future__ import annotations

from itertools import combinations
import math
from typing import Any, Iterable, Mapping

from modules.allocation_contract import (
    FeasibilityStatus,
    MultiSupplierAllocationRequest,
    MultiSupplierFeasibilityResult,
    SupplierAllocationInput,
    normalize_supplier_id,
)

MAX_COMBINATIONS_EVALUATED = 5000


def _records(source: Any) -> list[Mapping[str, Any]]:
    if hasattr(source, "to_dict"):
        try:
            return list(source.copy(deep=True).to_dict(orient="records"))
        except TypeError:
            pass
    return [dict(item) for item in source]


def _result(
    request: MultiSupplierAllocationRequest,
    status: FeasibilityStatus,
    summary: str,
    *,
    eligible_count: int = 0,
    feasible_supplier_count: int = 0,
    evidence: tuple[Mapping[str, Any], ...] = (),
    maximum_shares: Mapping[str, float] | None = None,
    blocking: Iterable[str] = (),
    warnings: Iterable[str] = (),
    feasible_combinations: tuple[tuple[str, ...], ...] = (),
    binding: Iterable[str] = (),
    enumeration_policy: str = "complete_deterministic_enumeration",
    combinations_evaluated: int = 0,
    truncated: bool = False,
) -> MultiSupplierFeasibilityResult:
    return MultiSupplierFeasibilityResult(
        feasible=status is FeasibilityStatus.FEASIBLE,
        status_code=status,
        summary=summary,
        eligible_supplier_count=eligible_count,
        required_awardee_count=request.required_awardee_count,
        feasible_supplier_count=feasible_supplier_count,
        supplier_capacity_evidence=evidence,
        maximum_feasible_share_by_supplier=dict(sorted((maximum_shares or {}).items())),
        blocking_reasons=tuple(sorted(set(blocking))),
        warnings=tuple(sorted(set(warnings))),
        feasible_supplier_combinations=feasible_combinations,
        binding_constraints=tuple(sorted(set(binding))),
        human_review_required=True,
        contract_version=request.contract_version,
        enumeration_policy=enumeration_policy,
        combinations_evaluated=combinations_evaluated,
        combinations_truncated=truncated,
    )


def _logical_request_errors(request: MultiSupplierAllocationRequest) -> tuple[FeasibilityStatus | None, list[str]]:
    errors: list[str] = []
    status: FeasibilityStatus | None = None
    k = request.required_awardee_count
    if k < 1:
        status = FeasibilityStatus.INVALID_REQUEST
        errors.append("required_awardee_count must be at least 1")
    if request.maximum_supplier_share_pct <= 0 or request.maximum_supplier_share_pct > 100:
        status = FeasibilityStatus.INVALID_REQUEST
        errors.append("maximum_supplier_share_pct must be greater than 0 and no greater than 100")
    if request.minimum_awarded_share_pct > request.maximum_supplier_share_pct:
        status = FeasibilityStatus.SHARE_CONSTRAINT_CONFLICT
        errors.append("minimum_awarded_share_pct cannot exceed maximum_supplier_share_pct")
    if request.minimum_continuity_share_pct > request.maximum_supplier_share_pct:
        status = FeasibilityStatus.SHARE_CONSTRAINT_CONFLICT
        errors.append("minimum_continuity_share_pct cannot exceed maximum_supplier_share_pct")
    if k * request.minimum_awarded_share_pct > 100 + 1e-9:
        status = FeasibilityStatus.SHARE_CONSTRAINT_CONFLICT
        errors.append("required_awardee_count multiplied by minimum_awarded_share_pct exceeds 100%")
    if k * request.maximum_supplier_share_pct < 100 - 1e-9:
        status = FeasibilityStatus.SHARE_CONSTRAINT_CONFLICT
        errors.append("required_awardee_count multiplied by maximum_supplier_share_pct cannot cover 100%")
    if request.capacity_utilization_ceiling_pct <= 0 or request.capacity_utilization_ceiling_pct > 100:
        status = FeasibilityStatus.INVALID_REQUEST
        errors.append("capacity_utilization_ceiling_pct must be greater than 0 and no greater than 100")
    if request.minimum_risk_score > 100 or request.minimum_esg_score > 100:
        status = FeasibilityStatus.INVALID_REQUEST
        errors.append("risk and ESG thresholds cannot exceed 100")
    return status, errors


def _normalize_suppliers(source: Any) -> tuple[list[SupplierAllocationInput], list[str], list[str]]:
    suppliers: list[SupplierAllocationInput] = []
    invalid_capacity: list[str] = []
    invalid_records: list[str] = []
    for index, record in enumerate(_records(source)):
        raw_id = record.get("supplier_id", record.get("Supplier", record.get("supplier_name", f"row-{index + 1}")))
        try:
            supplier_id = normalize_supplier_id(raw_id)
        except ValueError as exc:
            invalid_records.append(f"row {index + 1}: {exc}")
            continue
        capacity = record.get("supplier_capacity", record.get("Supplier Capacity"))
        if capacity is None or isinstance(capacity, bool) or not isinstance(capacity, (int, float)):
            invalid_capacity.append(f"{supplier_id}: missing or non-numeric supplier capacity")
            record = dict(record)
            record["supplier_capacity"] = None
        elif not math.isfinite(float(capacity)) or float(capacity) <= 0:
            invalid_capacity.append(f"{supplier_id}: supplier capacity must be finite and greater than zero")
            record = dict(record)
            record["supplier_capacity"] = None
        try:
            suppliers.append(SupplierAllocationInput.from_mapping(record))
        except ValueError as exc:
            invalid_records.append(f"{supplier_id}: {exc}")
    identifiers = [item.supplier_id for item in suppliers]
    duplicates = sorted({item for item in identifiers if identifiers.count(item) > 1})
    if duplicates:
        invalid_records.append("duplicate supplier identifiers: " + ", ".join(duplicates))
    return sorted(suppliers, key=lambda item: item.supplier_id), sorted(invalid_capacity), sorted(invalid_records)


def evaluate_allocation_feasibility(
    request: MultiSupplierAllocationRequest,
    supplier_records: Any,
    *,
    max_combinations: int = MAX_COMBINATIONS_EVALUATED,
) -> MultiSupplierFeasibilityResult:
    """Evaluate whether at least one deterministic exactly-K supplier portfolio can cover demand."""
    request_status, request_errors = _logical_request_errors(request)
    if request_status is not None:
        return _result(request, request_status, "Allocation request is not feasible.", blocking=request_errors)
    if isinstance(max_combinations, bool) or not isinstance(max_combinations, int) or max_combinations < 1:
        return _result(
            request,
            FeasibilityStatus.INVALID_REQUEST,
            "Allocation request is not feasible.",
            blocking=("max_combinations must be a positive integer",),
        )

    suppliers, invalid_capacity, invalid_records = _normalize_suppliers(supplier_records)
    if invalid_records:
        return _result(
            request,
            FeasibilityStatus.INVALID_REQUEST,
            "Supplier inputs contain invalid governed values.",
            blocking=invalid_records,
        )

    supplier_ids = {item.supplier_id for item in suppliers}
    required = set(request.required_supplier_ids)
    excluded = set(request.excluded_supplier_ids)
    conflict = sorted(required & excluded)
    if conflict:
        return _result(
            request,
            FeasibilityStatus.REQUIRED_EXCLUDED_CONFLICT,
            "A required supplier is also excluded.",
            blocking=("Required and excluded supplier conflict: " + ", ".join(conflict),),
        )
    missing_required = sorted(required - supplier_ids)
    if missing_required:
        return _result(
            request,
            FeasibilityStatus.REQUIRED_SUPPLIER_MISSING,
            "One or more required suppliers are missing.",
            blocking=("Missing required suppliers: " + ", ".join(missing_required),),
        )
    if len(required) > request.required_awardee_count:
        return _result(
            request,
            FeasibilityStatus.INVALID_REQUEST,
            "Required supplier count exceeds required awardee count.",
            blocking=("required_supplier_ids cannot contain more suppliers than required_awardee_count",),
        )

    commercially_eligible = [
        item
        for item in suppliers
        if item.technical_eligible
        and item.risk_score >= request.minimum_risk_score
        and item.esg_score >= request.minimum_esg_score
        and item.supplier_id not in excluded
    ]
    eligible_ids = {item.supplier_id for item in commercially_eligible}
    ineligible_required = sorted(required - eligible_ids)
    if ineligible_required:
        return _result(
            request,
            FeasibilityStatus.REQUIRED_SUPPLIER_INELIGIBLE,
            "One or more required suppliers do not satisfy eligibility thresholds.",
            eligible_count=len(commercially_eligible),
            blocking=("Required suppliers not eligible: " + ", ".join(ineligible_required),),
        )
    if len(commercially_eligible) < request.required_awardee_count:
        return _result(
            request,
            FeasibilityStatus.INSUFFICIENT_ELIGIBLE_SUPPLIERS,
            "Eligible supplier count is below the required awardee count.",
            eligible_count=len(commercially_eligible),
            blocking=(
                f"Required {request.required_awardee_count} awardees but only {len(commercially_eligible)} suppliers are eligible",
            ),
        )

    relevant_invalid_capacity = [
        reason for reason in invalid_capacity if reason.split(":", 1)[0] in eligible_ids
    ]
    evidence = []
    maximum_shares: dict[str, float] = {}
    ceiling = request.capacity_utilization_ceiling_pct / 100.0
    for supplier in commercially_eligible:
        capacity = supplier.supplier_capacity
        capacity_share = 0.0 if capacity is None else capacity * ceiling / request.annual_volume * 100.0
        maximum_share = min(request.maximum_supplier_share_pct, capacity_share)
        maximum_shares[supplier.supplier_id] = round(maximum_share, 10)
        evidence.append(
            {
                "supplier_id": supplier.supplier_id,
                "capacity_supplied": capacity is not None,
                "supplier_capacity": capacity,
                "capacity_utilization_ceiling_pct": request.capacity_utilization_ceiling_pct,
                "capacity_supported_share_pct": round(capacity_share, 10),
                "maximum_feasible_share_pct": round(maximum_share, 10),
                "capacity_verified": False,
            }
        )
    evidence_tuple = tuple(sorted(evidence, key=lambda item: str(item["supplier_id"])))
    if relevant_invalid_capacity:
        return _result(
            request,
            FeasibilityStatus.MISSING_CAPACITY_EVIDENCE,
            "Eligible supplier capacity evidence is missing or invalid; no capacity was inferred.",
            eligible_count=len(commercially_eligible),
            feasible_supplier_count=sum(
                share + 1e-9 >= request.minimum_awarded_share_pct for share in maximum_shares.values()
            ),
            evidence=evidence_tuple,
            maximum_shares=maximum_shares,
            blocking=relevant_invalid_capacity,
            binding=("supplier capacity evidence",),
        )

    minimum = request.minimum_awarded_share_pct
    capable = [item for item in commercially_eligible if maximum_shares[item.supplier_id] + 1e-9 >= minimum]
    if len(capable) < request.required_awardee_count:
        return _result(
            request,
            FeasibilityStatus.INSUFFICIENT_CAPACITY,
            "Fewer than K eligible suppliers can support the minimum awarded share.",
            eligible_count=len(commercially_eligible),
            feasible_supplier_count=len(capable),
            evidence=evidence_tuple,
            maximum_shares=maximum_shares,
            blocking=(
                f"Only {len(capable)} suppliers can support the {minimum:g}% minimum share required for {request.required_awardee_count} awardees",
            ),
            binding=("minimum awarded share", "supplier capacity"),
        )

    required_tuple = tuple(sorted(required))
    candidate_ids = tuple(item.supplier_id for item in capable)
    available_optional = tuple(item for item in candidate_ids if item not in required)
    slots = request.required_awardee_count - len(required_tuple)
    feasible: list[tuple[str, ...]] = []
    evaluated = 0
    truncated = False
    policy = "complete_deterministic_enumeration"
    for optional in combinations(available_optional, slots):
        if evaluated >= max_combinations:
            truncated = True
            policy = f"bounded_deterministic_enumeration_first_{max_combinations}"
            break
        portfolio = tuple(sorted(required_tuple + optional))
        evaluated += 1
        maximum_total = sum(maximum_shares[item] for item in portfolio)
        continuity_floor = max(minimum, request.minimum_continuity_share_pct)
        continuity_capable = sum(maximum_shares[item] + 1e-9 >= continuity_floor for item in portfolio)
        continuity_ok = request.required_awardee_count == 1 or continuity_capable >= request.required_awardee_count - 1
        if maximum_total + 1e-9 >= 100.0 and continuity_ok:
            feasible.append(portfolio)

    if not feasible:
        total_capacity_share = sum(sorted(maximum_shares.values(), reverse=True)[: request.required_awardee_count])
        status = (
            FeasibilityStatus.INSUFFICIENT_CAPACITY
            if total_capacity_share + 1e-9 < 100.0
            else FeasibilityStatus.NO_FEASIBLE_K_SUPPLIER_PORTFOLIO
        )
        reasons = [
            f"No exactly-{request.required_awardee_count} supplier portfolio satisfies all share and capacity constraints"
        ]
        if truncated:
            reasons.append("Combination evaluation reached the disclosed deterministic bound")
        return _result(
            request,
            status,
            "No feasible exactly-K supplier portfolio was found.",
            eligible_count=len(commercially_eligible),
            feasible_supplier_count=len(capable),
            evidence=evidence_tuple,
            maximum_shares=maximum_shares,
            blocking=reasons,
            warnings=("Supplier capacity is supplied evidence and has not been independently verified.",),
            binding=("supplier capacity", "awardee count", "share constraints"),
            enumeration_policy=policy,
            combinations_evaluated=evaluated,
            truncated=truncated,
        )

    return _result(
        request,
        FeasibilityStatus.FEASIBLE,
        f"At least one feasible exactly-{request.required_awardee_count} supplier portfolio can cover 100% of demand.",
        eligible_count=len(commercially_eligible),
        feasible_supplier_count=len(capable),
        evidence=evidence_tuple,
        maximum_shares=maximum_shares,
        warnings=(
            "Feasibility is decision support only; supplier capacity is not independently verified.",
            "Human procurement approval remains mandatory.",
        ),
        feasible_combinations=tuple(feasible),
        binding=("exact awardee count", "supplier capacity", "minimum and maximum share"),
        enumeration_policy=policy,
        combinations_evaluated=evaluated,
        truncated=truncated,
    )
