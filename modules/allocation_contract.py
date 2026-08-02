"""Versioned immutable contracts for governed multi-supplier allocation feasibility."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
import json
import math
from types import MappingProxyType
from typing import Any, Mapping, Sequence

ALLOCATION_CONTRACT_VERSION = "AIPC-MULTI-ALLOC-1.0"
CONTINUITY_SHARE_INTERPRETATION = (
    "minimum share per continuity supplier; for K greater than 1, at least K-1 awarded suppliers "
    "must each be capable of this share"
)


class FeasibilityStatus(str, Enum):
    FEASIBLE = "FEASIBLE"
    ENUMERATION_LIMIT_REACHED = "ENUMERATION_LIMIT_REACHED"
    INVALID_REQUEST = "INVALID_REQUEST"
    INSUFFICIENT_ELIGIBLE_SUPPLIERS = "INSUFFICIENT_ELIGIBLE_SUPPLIERS"
    SHARE_CONSTRAINT_CONFLICT = "SHARE_CONSTRAINT_CONFLICT"
    INSUFFICIENT_CAPACITY = "INSUFFICIENT_CAPACITY"
    REQUIRED_SUPPLIER_INELIGIBLE = "REQUIRED_SUPPLIER_INELIGIBLE"
    REQUIRED_SUPPLIER_MISSING = "REQUIRED_SUPPLIER_MISSING"
    REQUIRED_EXCLUDED_CONFLICT = "REQUIRED_EXCLUDED_CONFLICT"
    MISSING_CAPACITY_EVIDENCE = "MISSING_CAPACITY_EVIDENCE"
    NO_FEASIBLE_K_SUPPLIER_PORTFOLIO = "NO_FEASIBLE_K_SUPPLIER_PORTFOLIO"


def normalize_supplier_id(value: Any) -> str:
    text = " ".join(str(value or "").strip().split())
    if not text:
        raise ValueError("supplier_id or supplier name is required")
    return text.casefold()


def normalize_controlled_bool(value: Any, label: str = "technical_eligible") -> bool:
    """Normalize only explicit governed boolean representations."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int) and not isinstance(value, bool) and value in {0, 1}:
        return bool(value)
    if isinstance(value, str):
        normalized = " ".join(value.strip().casefold().split())
        if normalized in {"true", "yes", "1", "eligible"}:
            return True
        if normalized in {"false", "no", "0", "ineligible"}:
            return False
    raise ValueError(f"{label} must be an explicit governed boolean value")


def _finite_number(value: Any, label: str, *, positive: bool = False, non_negative: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite numeric value")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} must be a finite numeric value")
    if positive and result <= 0:
        raise ValueError(f"{label} must be greater than zero")
    if non_negative and result < 0:
        raise ValueError(f"{label} must be non-negative")
    return result


def _normalized_ids(values: Sequence[str] | None) -> tuple[str, ...]:
    return tuple(sorted({normalize_supplier_id(item) for item in (values or ())}))


def _deep_freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _deep_freeze(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))})
    if isinstance(value, (list, tuple, set, frozenset)):
        return tuple(_deep_freeze(item) for item in value)
    return value


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _thaw(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    if isinstance(value, Enum):
        return value.value
    return value


@dataclass(frozen=True, slots=True)
class MultiSupplierAllocationRequest:
    annual_volume: float
    annual_volume_unit: str
    required_awardee_count: int
    minimum_awarded_share_pct: float
    maximum_supplier_share_pct: float
    minimum_continuity_share_pct: float
    minimum_risk_score: float
    minimum_esg_score: float
    capacity_utilization_ceiling_pct: float
    category: str
    commodity: str
    comparison_currency: str = "USD"
    required_supplier_ids: tuple[str, ...] = field(default_factory=tuple)
    excluded_supplier_ids: tuple[str, ...] = field(default_factory=tuple)
    contract_version: str = ALLOCATION_CONTRACT_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "annual_volume", _finite_number(self.annual_volume, "annual_volume", positive=True))
        if isinstance(self.required_awardee_count, bool) or not isinstance(self.required_awardee_count, int):
            raise ValueError("required_awardee_count must be an integer")
        for name in (
            "minimum_awarded_share_pct", "maximum_supplier_share_pct", "minimum_continuity_share_pct",
            "minimum_risk_score", "minimum_esg_score", "capacity_utilization_ceiling_pct",
        ):
            object.__setattr__(self, name, _finite_number(getattr(self, name), name, non_negative=True))
        for name in ("annual_volume_unit", "category", "commodity", "comparison_currency"):
            value = " ".join(str(getattr(self, name) or "").strip().split())
            if not value:
                raise ValueError(f"{name} is required")
            object.__setattr__(self, name, value)
        if self.contract_version != ALLOCATION_CONTRACT_VERSION:
            raise ValueError(f"Unsupported contract_version '{self.contract_version}'")
        object.__setattr__(self, "required_supplier_ids", _normalized_ids(self.required_supplier_ids))
        object.__setattr__(self, "excluded_supplier_ids", _normalized_ids(self.excluded_supplier_ids))

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["required_supplier_ids"] = list(self.required_supplier_ids)
        payload["excluded_supplier_ids"] = list(self.excluded_supplier_ids)
        return payload

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"), allow_nan=False)


@dataclass(frozen=True, slots=True)
class SupplierAllocationInput:
    supplier_id: str
    technical_eligible: bool
    adjusted_tco_unit_usd: float
    total_score: float
    risk_score: float
    performance_score: float
    esg_score: float
    supplier_capacity: float | None
    eligibility_failure_reasons: tuple[str, ...] = field(default_factory=tuple)
    category_specific_eligibility_evidence: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "supplier_id", normalize_supplier_id(self.supplier_id))
        object.__setattr__(self, "technical_eligible", normalize_controlled_bool(self.technical_eligible))
        for name in ("adjusted_tco_unit_usd", "total_score", "risk_score", "performance_score", "esg_score"):
            object.__setattr__(self, name, _finite_number(getattr(self, name), name, non_negative=True))
        if self.supplier_capacity is not None:
            object.__setattr__(self, "supplier_capacity", _finite_number(self.supplier_capacity, "supplier_capacity", non_negative=True))
        reasons = tuple(sorted({" ".join(str(item).strip().split()) for item in self.eligibility_failure_reasons if str(item).strip()}))
        object.__setattr__(self, "eligibility_failure_reasons", reasons)
        object.__setattr__(self, "category_specific_eligibility_evidence", _deep_freeze(self.category_specific_eligibility_evidence or {}))

    @classmethod
    def from_mapping(cls, record: Mapping[str, Any]) -> "SupplierAllocationInput":
        supplier_id = record.get("supplier_id", record.get("Supplier", record.get("supplier_name")))
        capacity = record.get("supplier_capacity", record.get("Supplier Capacity"))
        reasons = record.get("eligibility_failure_reasons", record.get("technical_ineligibility_reasons", ()))
        if isinstance(reasons, str):
            reasons = (reasons,)
        return cls(
            supplier_id=supplier_id,
            technical_eligible=record.get("technical_eligible", True),
            adjusted_tco_unit_usd=record.get("adjusted_tco_unit_usd", 0.0),
            total_score=record.get("total_score", 0.0),
            risk_score=record.get("risk_score", 0.0),
            performance_score=record.get("performance_score", 0.0),
            esg_score=record.get("esg_score", 0.0),
            supplier_capacity=capacity,
            eligibility_failure_reasons=tuple(reasons or ()),
            category_specific_eligibility_evidence=record.get("category_specific_eligibility_evidence", {}),
        )


@dataclass(frozen=True, slots=True)
class MultiSupplierFeasibilityResult:
    feasible: bool
    status_code: FeasibilityStatus
    summary: str
    eligible_supplier_count: int
    required_awardee_count: int
    feasible_supplier_count: int
    supplier_capacity_evidence: tuple[Mapping[str, Any], ...]
    maximum_feasible_share_by_supplier: Mapping[str, float]
    blocking_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    feasible_supplier_combinations: tuple[tuple[str, ...], ...]
    binding_constraints: tuple[str, ...]
    human_review_required: bool = True
    contract_version: str = ALLOCATION_CONTRACT_VERSION
    enumeration_policy: str = "complete_deterministic_enumeration"
    combinations_evaluated: int = 0
    combinations_truncated: bool = False
    decision_complete: bool = True
    continuity_share_interpretation: str = CONTINUITY_SHARE_INTERPRETATION

    def __post_init__(self) -> None:
        object.__setattr__(self, "supplier_capacity_evidence", tuple(_deep_freeze(item) for item in self.supplier_capacity_evidence))
        object.__setattr__(self, "maximum_feasible_share_by_supplier", _deep_freeze(self.maximum_feasible_share_by_supplier))

    def to_dict(self) -> dict[str, Any]:
        return {
            "feasible": self.feasible,
            "status_code": self.status_code.value,
            "summary": self.summary,
            "eligible_supplier_count": self.eligible_supplier_count,
            "required_awardee_count": self.required_awardee_count,
            "feasible_supplier_count": self.feasible_supplier_count,
            "supplier_capacity_evidence": [_thaw(item) for item in self.supplier_capacity_evidence],
            "maximum_feasible_share_by_supplier": _thaw(self.maximum_feasible_share_by_supplier),
            "blocking_reasons": list(self.blocking_reasons),
            "warnings": list(self.warnings),
            "feasible_supplier_combinations": [list(item) for item in self.feasible_supplier_combinations],
            "binding_constraints": list(self.binding_constraints),
            "human_review_required": self.human_review_required,
            "contract_version": self.contract_version,
            "enumeration_policy": self.enumeration_policy,
            "combinations_evaluated": self.combinations_evaluated,
            "combinations_truncated": self.combinations_truncated,
            "decision_complete": self.decision_complete,
            "continuity_share_interpretation": self.continuity_share_interpretation,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"), allow_nan=False)
