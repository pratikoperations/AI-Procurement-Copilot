"""Isolated governed adapter for constructing multi-supplier allocation contracts."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
import json
import math
from numbers import Integral, Real
from types import MappingProxyType
from typing import Any, Mapping, Sequence

import pandas as pd

from modules.allocation_contract import (
    ALLOCATION_CONTRACT_VERSION,
    MultiSupplierAllocationRequest,
    SupplierAllocationInput,
    normalize_controlled_bool,
    normalize_supplier_id,
)

ADAPTER_VERSION = "AIPC-MULTI-ALLOC-ADAPTER-1.0"
SUPPORTED_SOURCE_TYPES = frozenset(
    {"synthetic_demo", "uploaded_rfq", "governed_workbook", "steel_synthetic", "category_adapter"}
)
SUPPORTED_EVIDENCE_ORIGINS = frozenset({"controlled_synthetic", "supplied", "governed_workbook"})
DEFAULT_EVIDENCE_ORIGIN_BY_SOURCE = MappingProxyType(
    {
        "synthetic_demo": "controlled_synthetic",
        "steel_synthetic": "controlled_synthetic",
        "uploaded_rfq": "supplied",
        "governed_workbook": "governed_workbook",
    }
)
SUPPORTED_UNITS = frozenset(
    {"unit", "units", "piece", "pieces", "kg", "kilogram", "kilograms", "mt", "tonne", "tonnes"}
)
CANONICAL_COLUMNS = MappingProxyType(
    {
        "supplier_id": "Supplier",
        "technical_eligible": "technical_eligible",
        "adjusted_tco_unit_usd": "adjusted_tco_unit_usd",
        "total_score": "total_score",
        "risk_score": "risk_score",
        "performance_score": "performance_score",
        "esg_score": "esg_score",
        "supplier_capacity": "Supplier Capacity",
    }
)
STEEL_ALIASES = MappingProxyType(
    {
        "adjusted_tco_unit_usd": "normalized_usd_per_kg",
        "total_score": "governed_total_score",
    }
)
ELIGIBILITY_REASON_COLUMNS = ("technical_ineligibility_reasons", "eligibility_failure_reasons")
CATEGORY_EVIDENCE_COLUMNS = (
    "Laminate Structure", "Application Approval Status", "Application Approval",
    "Print Process", "Adhesive Type", "GSM", "Strength Grade", "Kraft Variant",
    "Mill Allocation %", "Quality Continuity Score", "Supported Steel Profiles",
    "Thickness Min mm", "Thickness Max mm", "Width Min mm", "Width Max mm",
    "Zinc Capability Max g/m²", "Paint Line Capability", "Supplier or Mill Approval",
    "Test Certificate Availability", "steel_profile", "governed_rank",
)
_MISSING = object()


class AdapterStatus(str, Enum):
    ADAPTER_READY = "ADAPTER_READY"
    INVALID_ROUTE_INPUT = "INVALID_ROUTE_INPUT"
    MISSING_REQUIRED_COLUMN = "MISSING_REQUIRED_COLUMN"
    MISSING_TECHNICAL_ELIGIBILITY = "MISSING_TECHNICAL_ELIGIBILITY"
    AMBIGUOUS_TECHNICAL_ELIGIBILITY = "AMBIGUOUS_TECHNICAL_ELIGIBILITY"
    MISSING_SUPPLIER_CAPACITY = "MISSING_SUPPLIER_CAPACITY"
    INVALID_SUPPLIER_CAPACITY = "INVALID_SUPPLIER_CAPACITY"
    MISSING_SCORE_EVIDENCE = "MISSING_SCORE_EVIDENCE"
    MISSING_TCO_EVIDENCE = "MISSING_TCO_EVIDENCE"
    DUPLICATE_SUPPLIER_ID = "DUPLICATE_SUPPLIER_ID"
    UNSUPPORTED_UNIT = "UNSUPPORTED_UNIT"
    UNSUPPORTED_CURRENCY_BASIS = "UNSUPPORTED_CURRENCY_BASIS"
    CONTRACT_CONSTRUCTION_FAILURE = "CONTRACT_CONSTRUCTION_FAILURE"


class EvidenceNormalizationError(ValueError):
    """Raised when category evidence cannot be represented deterministically."""

    def __init__(self, value: Any) -> None:
        value_type = f"{type(value).__module__}.{type(value).__qualname__}"
        super().__init__(f"unsupported evidence type '{value_type}'")
        self.value_type = value_type


def _is_missing_scalar(value: Any) -> bool:
    if value is None:
        return True
    try:
        missing = pd.isna(value)
    except (TypeError, ValueError):
        return False
    if isinstance(missing, bool):
        return missing
    if type(missing).__module__.startswith("numpy") and type(missing).__name__ == "bool_":
        return bool(missing)
    return False


def _json_safe(value: Any) -> Any:
    """Return a deterministic strict-JSON representation or raise for unsupported evidence."""
    if isinstance(value, Mapping):
        normalized: dict[str, Any] = {}
        for key, item in sorted(value.items(), key=lambda pair: str(pair[0])):
            safe_item = _json_safe(item)
            if safe_item is not _MISSING:
                normalized[str(key)] = safe_item
        return normalized
    if isinstance(value, (list, tuple, set, frozenset)):
        items = [_json_safe(item) for item in value]
        filtered = [item for item in items if item is not _MISSING]
        if isinstance(value, (set, frozenset)):
            return sorted(filtered, key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":")))
        return filtered
    if isinstance(value, Enum):
        return value.value
    if _is_missing_scalar(value):
        return _MISSING
    if isinstance(value, bool):
        return bool(value)
    if isinstance(value, Integral):
        return int(value)
    if isinstance(value, Real):
        number = float(value)
        return number if math.isfinite(number) else _MISSING
    if isinstance(value, (datetime, date, pd.Timestamp)):
        return value.isoformat()
    if isinstance(value, str):
        return value
    if hasattr(value, "item"):
        try:
            scalar = value.item()
        except (TypeError, ValueError):
            scalar = value
        if scalar is not value:
            return _json_safe(scalar)
    if hasattr(value, "to_dict"):
        try:
            mapped = value.to_dict()
        except (TypeError, ValueError, AttributeError) as exc:
            raise EvidenceNormalizationError(value) from exc
        return _json_safe(mapped)
    raise EvidenceNormalizationError(value)


def _freeze(value: Any) -> Any:
    safe = _json_safe(value)
    if safe is _MISSING:
        return None
    if isinstance(safe, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in safe.items()})
    if isinstance(safe, list):
        return tuple(_freeze(item) for item in safe)
    return safe


def _thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _thaw(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "to_dict"):
        return _json_safe(value.to_dict())
    safe = _json_safe(value)
    return None if safe is _MISSING else safe


def _clean_text(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _finite(value: Any, label: str, *, positive: bool = False, non_negative: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{label} must be a finite numeric value")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} must be a finite numeric value")
    if positive and result <= 0:
        raise ValueError(f"{label} must be greater than zero")
    if non_negative and result < 0:
        raise ValueError(f"{label} must be non-negative")
    return result


def _reason_tuple(value: Any) -> tuple[str, ...]:
    if _is_missing_scalar(value):
        return ()
    values = value if isinstance(value, (list, tuple, set, frozenset)) else (value,)
    return tuple(sorted({_clean_text(item) for item in values if not _is_missing_scalar(item) and _clean_text(item)}))


def _resolve_evidence_origin(source_type: str, evidence_origin: str | None) -> str:
    supplied = _clean_text(evidence_origin).casefold().replace(" ", "_") if evidence_origin is not None else ""
    if supplied and supplied not in SUPPORTED_EVIDENCE_ORIGINS:
        raise ValueError(f"Unsupported evidence_origin '{supplied}'")
    if source_type == "category_adapter":
        if not supplied:
            raise ValueError("category_adapter requires explicit evidence_origin")
        return supplied
    required = DEFAULT_EVIDENCE_ORIGIN_BY_SOURCE[source_type]
    if supplied and supplied != required:
        raise ValueError(f"source_type '{source_type}' requires evidence_origin '{required}'")
    return required


def _evidence_class(origin: str) -> str:
    return {
        "controlled_synthetic": "controlled synthetic",
        "supplied": "supplied",
        "governed_workbook": "governed workbook",
    }[origin]


def _evidence_note(origin: str, subject: str = "route") -> str:
    if origin == "controlled_synthetic":
        return "Controlled synthetic demonstration assumption; not verified supplier evidence."
    if origin == "governed_workbook":
        return f"Governed-workbook {subject} evidence; independent verification is not claimed."
    return f"Supplied {subject} evidence; independent verification is not claimed."


@dataclass(frozen=True, slots=True)
class MultiSupplierAllocationAdapterResult:
    adapter_version: str
    ready: bool
    status_code: AdapterStatus
    summary: str
    request: MultiSupplierAllocationRequest | None
    supplier_inputs: tuple[SupplierAllocationInput, ...]
    route_name: str
    category: str
    commodity: str
    source_type: str
    field_provenance: tuple[Mapping[str, Any], ...]
    eligibility_evidence: tuple[Mapping[str, Any], ...]
    capacity_evidence: tuple[Mapping[str, Any], ...]
    blocking_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    controlled_defaults_used: tuple[str, ...]
    human_review_required: bool = True

    def __post_init__(self) -> None:
        if self.adapter_version != ADAPTER_VERSION:
            raise ValueError(f"Unsupported adapter_version '{self.adapter_version}'")
        object.__setattr__(self, "supplier_inputs", tuple(self.supplier_inputs))
        object.__setattr__(self, "field_provenance", tuple(_freeze(item) for item in self.field_provenance))
        object.__setattr__(self, "eligibility_evidence", tuple(_freeze(item) for item in self.eligibility_evidence))
        object.__setattr__(self, "capacity_evidence", tuple(_freeze(item) for item in self.capacity_evidence))
        object.__setattr__(self, "blocking_reasons", tuple(sorted(set(str(item) for item in self.blocking_reasons))))
        object.__setattr__(self, "warnings", tuple(sorted(set(str(item) for item in self.warnings))))
        object.__setattr__(self, "controlled_defaults_used", tuple(sorted(set(str(item) for item in self.controlled_defaults_used))))

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "adapter_version": self.adapter_version,
            "ready": self.ready,
            "status_code": self.status_code.value,
            "summary": self.summary,
            "request": None if self.request is None else self.request.to_dict(),
            "supplier_inputs": [
                {
                    "supplier_id": item.supplier_id,
                    "technical_eligible": item.technical_eligible,
                    "adjusted_tco_unit_usd": item.adjusted_tco_unit_usd,
                    "total_score": item.total_score,
                    "risk_score": item.risk_score,
                    "performance_score": item.performance_score,
                    "esg_score": item.esg_score,
                    "supplier_capacity": item.supplier_capacity,
                    "eligibility_failure_reasons": list(item.eligibility_failure_reasons),
                    "category_specific_eligibility_evidence": _thaw(item.category_specific_eligibility_evidence),
                }
                for item in self.supplier_inputs
            ],
            "route_name": self.route_name,
            "category": self.category,
            "commodity": self.commodity,
            "source_type": self.source_type,
            "field_provenance": [_thaw(item) for item in self.field_provenance],
            "eligibility_evidence": [_thaw(item) for item in self.eligibility_evidence],
            "capacity_evidence": [_thaw(item) for item in self.capacity_evidence],
            "blocking_reasons": list(self.blocking_reasons),
            "warnings": list(self.warnings),
            "controlled_defaults_used": list(self.controlled_defaults_used),
            "human_review_required": self.human_review_required,
        }
        safe = _json_safe(payload)
        if safe is _MISSING:
            raise ValueError("Adapter result could not be normalized for strict JSON serialization")
        return safe

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"), allow_nan=False)


def _result(
    status: AdapterStatus,
    summary: str,
    *,
    route_name: str,
    category: str,
    commodity: str,
    source_type: str,
    request: MultiSupplierAllocationRequest | None = None,
    supplier_inputs: Sequence[SupplierAllocationInput] = (),
    field_provenance: Sequence[Mapping[str, Any]] = (),
    eligibility_evidence: Sequence[Mapping[str, Any]] = (),
    capacity_evidence: Sequence[Mapping[str, Any]] = (),
    blocking_reasons: Sequence[str] = (),
    warnings: Sequence[str] = (),
    controlled_defaults_used: Sequence[str] = (),
) -> MultiSupplierAllocationAdapterResult:
    return MultiSupplierAllocationAdapterResult(
        adapter_version=ADAPTER_VERSION,
        ready=status is AdapterStatus.ADAPTER_READY,
        status_code=status,
        summary=summary,
        request=request,
        supplier_inputs=tuple(supplier_inputs),
        route_name=route_name,
        category=category,
        commodity=commodity,
        source_type=source_type,
        field_provenance=tuple(field_provenance),
        eligibility_evidence=tuple(eligibility_evidence),
        capacity_evidence=tuple(capacity_evidence),
        blocking_reasons=tuple(blocking_reasons),
        warnings=tuple(warnings),
        controlled_defaults_used=tuple(controlled_defaults_used),
        human_review_required=True,
    )


def _resolve_columns(
    dataframe: pd.DataFrame,
    source_type: str,
    aliases: Mapping[str, str] | None,
    evidence_origin: str,
) -> tuple[dict[str, str], tuple[Mapping[str, Any], ...], tuple[str, ...]]:
    explicit_aliases = dict(aliases or {})
    resolved: dict[str, str] = {}
    provenance: list[Mapping[str, Any]] = []
    missing: list[str] = []
    for canonical, exact in CANONICAL_COLUMNS.items():
        source_column = exact if exact in dataframe.columns else None
        mapping_type = "exact"
        if source_column is None and canonical in explicit_aliases:
            candidate = explicit_aliases[canonical]
            if candidate in dataframe.columns:
                source_column = candidate
                mapping_type = "explicit alias"
        if source_column is None and source_type == "steel_synthetic" and canonical in STEEL_ALIASES:
            candidate = STEEL_ALIASES[canonical]
            if candidate in dataframe.columns:
                source_column = candidate
                mapping_type = "category adapter"
        if source_column is None:
            missing.append(canonical)
            continue
        resolved[canonical] = source_column
        provenance.append(
            {
                "canonical_field": canonical,
                "source_column": source_column,
                "source_type": source_type,
                "mapping_type": mapping_type,
                "evidence_class": _evidence_class(evidence_origin),
                "blocking_state": False,
                "evidence_note": _evidence_note(evidence_origin),
            }
        )
    return resolved, tuple(sorted(provenance, key=lambda item: item["canonical_field"])), tuple(sorted(missing))


def _missing_status(missing: Sequence[str]) -> AdapterStatus:
    fields = set(missing)
    if "technical_eligible" in fields:
        return AdapterStatus.MISSING_TECHNICAL_ELIGIBILITY
    if "supplier_capacity" in fields:
        return AdapterStatus.MISSING_SUPPLIER_CAPACITY
    if "adjusted_tco_unit_usd" in fields:
        return AdapterStatus.MISSING_TCO_EVIDENCE
    if fields & {"total_score", "risk_score", "performance_score", "esg_score"}:
        return AdapterStatus.MISSING_SCORE_EVIDENCE
    return AdapterStatus.MISSING_REQUIRED_COLUMN


def build_multi_supplier_allocation_adapter(
    scored_df: pd.DataFrame,
    controls: Mapping[str, Any],
    *,
    route_name: str,
    source_type: str,
    column_aliases: Mapping[str, str] | None = None,
    evidence_origin: str | None = None,
) -> MultiSupplierAllocationAdapterResult:
    """Construct Gate 1 contracts without inferring missing eligibility, capacity, TCO, or scores."""
    route = _clean_text(route_name)
    source = _clean_text(source_type).casefold()
    category = _clean_text(controls.get("category")) if isinstance(controls, Mapping) else ""
    commodity = _clean_text(controls.get("commodity")) if isinstance(controls, Mapping) else ""

    if not isinstance(scored_df, pd.DataFrame) or scored_df.empty:
        return _result(
            AdapterStatus.INVALID_ROUTE_INPUT,
            "A non-empty scored supplier dataframe is required.",
            route_name=route,
            category=category,
            commodity=commodity,
            source_type=source,
            blocking_reasons=("scored_df must be a non-empty pandas DataFrame",),
        )
    if not isinstance(controls, Mapping) or not route or source not in SUPPORTED_SOURCE_TYPES:
        return _result(
            AdapterStatus.INVALID_ROUTE_INPUT,
            "Route name, supported source type, and governed controls are required.",
            route_name=route,
            category=category,
            commodity=commodity,
            source_type=source,
            blocking_reasons=("Invalid route_name, source_type, or controls mapping",),
        )
    try:
        origin = _resolve_evidence_origin(source, evidence_origin)
    except ValueError as exc:
        return _result(
            AdapterStatus.INVALID_ROUTE_INPUT,
            "A supported and source-consistent evidence origin is required.",
            route_name=route,
            category=category,
            commodity=commodity,
            source_type=source,
            blocking_reasons=(str(exc),),
        )

    currency = _clean_text(controls.get("comparison_currency", "USD")).upper()
    if currency != "USD":
        return _result(
            AdapterStatus.UNSUPPORTED_CURRENCY_BASIS,
            "Gate calculations require a USD comparison basis.",
            route_name=route, category=category, commodity=commodity, source_type=source,
            blocking_reasons=(f"Unsupported comparison currency '{currency}'",),
        )
    unit = _clean_text(controls.get("annual_volume_unit")).casefold()
    if unit not in SUPPORTED_UNITS:
        return _result(
            AdapterStatus.UNSUPPORTED_UNIT,
            "The governed annual-volume unit is missing or unsupported.",
            route_name=route, category=category, commodity=commodity, source_type=source,
            blocking_reasons=(f"Unsupported annual_volume_unit '{unit}'",),
        )

    resolved, provenance, missing = _resolve_columns(scored_df, source, column_aliases, origin)
    if missing:
        status = _missing_status(missing)
        reasons = tuple(f"Missing canonical field '{field}'" for field in missing)
        return _result(
            status,
            "Required allocation evidence is missing.",
            route_name=route, category=category, commodity=commodity, source_type=source,
            field_provenance=provenance, blocking_reasons=reasons,
        )

    try:
        request = MultiSupplierAllocationRequest(
            annual_volume=_finite(controls.get("annual_volume"), "annual_volume", positive=True),
            annual_volume_unit=_clean_text(controls.get("annual_volume_unit")),
            required_awardee_count=controls.get("required_awardee_count"),
            minimum_awarded_share_pct=controls.get("minimum_awarded_share_pct"),
            maximum_supplier_share_pct=controls.get("maximum_supplier_share_pct"),
            minimum_continuity_share_pct=controls.get("minimum_continuity_share_pct"),
            minimum_risk_score=controls.get("minimum_risk_score"),
            minimum_esg_score=controls.get("minimum_esg_score"),
            capacity_utilization_ceiling_pct=controls.get("capacity_utilization_ceiling_pct"),
            category=category,
            commodity=commodity,
            comparison_currency=currency,
            required_supplier_ids=tuple(controls.get("required_supplier_ids") or ()),
            excluded_supplier_ids=tuple(controls.get("excluded_supplier_ids") or ()),
            contract_version=ALLOCATION_CONTRACT_VERSION,
        )
    except (TypeError, ValueError) as exc:
        return _result(
            AdapterStatus.CONTRACT_CONSTRUCTION_FAILURE,
            "The governed allocation request could not be constructed.",
            route_name=route, category=category, commodity=commodity, source_type=source,
            field_provenance=provenance, blocking_reasons=(str(exc),),
        )

    suppliers: list[SupplierAllocationInput] = []
    eligibility_evidence: list[Mapping[str, Any]] = []
    capacity_evidence: list[Mapping[str, Any]] = []
    seen: set[str] = set()
    warnings: list[str] = []

    rows = scored_df.to_dict(orient="records")
    for row_index, row in enumerate(rows):
        try:
            supplier_id = normalize_supplier_id(row.get(resolved["supplier_id"]))
        except ValueError as exc:
            return _result(
                AdapterStatus.INVALID_ROUTE_INPUT,
                "A supplier identifier is missing or invalid.",
                route_name=route, category=category, commodity=commodity, source_type=source,
                request=request, field_provenance=provenance,
                eligibility_evidence=eligibility_evidence, capacity_evidence=capacity_evidence,
                blocking_reasons=(f"Row {row_index}: {exc}",),
            )
        if supplier_id in seen:
            return _result(
                AdapterStatus.DUPLICATE_SUPPLIER_ID,
                "Duplicate normalized supplier identifiers are not permitted.",
                route_name=route, category=category, commodity=commodity, source_type=source,
                request=request, field_provenance=provenance,
                eligibility_evidence=eligibility_evidence, capacity_evidence=capacity_evidence,
                blocking_reasons=(f"Row {row_index}, supplier '{supplier_id}': duplicate normalized identifier",),
            )
        seen.add(supplier_id)

        try:
            eligible = normalize_controlled_bool(
                row.get(resolved["technical_eligible"]),
                f"technical_eligible for {supplier_id}",
            )
        except ValueError as exc:
            return _result(
                AdapterStatus.AMBIGUOUS_TECHNICAL_ELIGIBILITY,
                "Technical eligibility contains an ambiguous value.",
                route_name=route, category=category, commodity=commodity, source_type=source,
                request=request, field_provenance=provenance,
                eligibility_evidence=eligibility_evidence, capacity_evidence=capacity_evidence,
                blocking_reasons=(f"Row {row_index}, supplier '{supplier_id}': {exc}",),
            )

        try:
            capacity = _finite(
                row.get(resolved["supplier_capacity"]),
                f"supplier_capacity for {supplier_id}",
                positive=True,
            )
        except ValueError as exc:
            return _result(
                AdapterStatus.INVALID_SUPPLIER_CAPACITY,
                "Supplier capacity must be explicit, finite, and greater than zero.",
                route_name=route, category=category, commodity=commodity, source_type=source,
                request=request, field_provenance=provenance,
                eligibility_evidence=eligibility_evidence, capacity_evidence=capacity_evidence,
                blocking_reasons=(f"Row {row_index}, supplier '{supplier_id}': {exc}",),
            )

        numeric_values: dict[str, float] = {}
        for canonical in ("adjusted_tco_unit_usd", "total_score", "risk_score", "performance_score", "esg_score"):
            try:
                numeric_values[canonical] = _finite(row.get(resolved[canonical]), canonical, non_negative=True)
            except ValueError as exc:
                status = AdapterStatus.MISSING_TCO_EVIDENCE if canonical == "adjusted_tco_unit_usd" else AdapterStatus.MISSING_SCORE_EVIDENCE
                return _result(
                    status,
                    "Required TCO or score evidence is invalid.",
                    route_name=route, category=category, commodity=commodity, source_type=source,
                    request=request, field_provenance=provenance,
                    eligibility_evidence=eligibility_evidence, capacity_evidence=capacity_evidence,
                    blocking_reasons=(f"Row {row_index}, supplier '{supplier_id}': {exc}",),
                )

        reason_values: list[str] = []
        for reason_column in ELIGIBILITY_REASON_COLUMNS:
            if reason_column in row:
                reason_values.extend(_reason_tuple(row.get(reason_column)))
        reasons = tuple(sorted(set(reason_values)))

        category_evidence: dict[str, Any] = {}
        for column in CATEGORY_EVIDENCE_COLUMNS:
            if column not in row:
                continue
            try:
                safe_value = _json_safe(row.get(column))
            except EvidenceNormalizationError as exc:
                return _result(
                    AdapterStatus.CONTRACT_CONSTRUCTION_FAILURE,
                    "Category evidence contains an unsupported value type.",
                    route_name=route, category=category, commodity=commodity, source_type=source,
                    request=request, field_provenance=provenance,
                    eligibility_evidence=eligibility_evidence, capacity_evidence=capacity_evidence,
                    blocking_reasons=(
                        f"Row {row_index}, supplier '{supplier_id}', field '{column}': {exc}",
                    ),
                )
            if safe_value is not _MISSING:
                category_evidence[column] = safe_value
        category_evidence.update(
            {
                "route_name": route,
                "source_type": source,
                "evidence_origin": origin,
                "evidence_class": _evidence_class(origin),
            }
        )

        supplier = SupplierAllocationInput(
            supplier_id=supplier_id,
            technical_eligible=eligible,
            adjusted_tco_unit_usd=numeric_values["adjusted_tco_unit_usd"],
            total_score=numeric_values["total_score"],
            risk_score=numeric_values["risk_score"],
            performance_score=numeric_values["performance_score"],
            esg_score=numeric_values["esg_score"],
            supplier_capacity=capacity,
            eligibility_failure_reasons=reasons,
            category_specific_eligibility_evidence=category_evidence,
        )
        suppliers.append(supplier)
        eligibility_evidence.append(
            {
                "supplier_id": supplier_id,
                "technical_eligible": eligible,
                "failure_reasons": reasons,
                "source_column": resolved["technical_eligible"],
                "evidence_origin": origin,
                "evidence_note": _evidence_note(origin, "eligibility"),
            }
        )
        capacity_evidence.append(
            {
                "supplier_id": supplier_id,
                "supplier_capacity": capacity,
                "annual_volume_unit": request.annual_volume_unit,
                "source_column": resolved["supplier_capacity"],
                "evidence_origin": origin,
                "evidence_note": _evidence_note(origin, "capacity"),
            }
        )

    suppliers = sorted(suppliers, key=lambda item: item.supplier_id)
    eligibility_evidence = sorted(eligibility_evidence, key=lambda item: item["supplier_id"])
    capacity_evidence = sorted(capacity_evidence, key=lambda item: item["supplier_id"])
    if origin == "controlled_synthetic":
        warnings.append(_evidence_note(origin))
    warnings.append("Adapter construction is decision support only; human procurement approval remains mandatory.")

    return _result(
        AdapterStatus.ADAPTER_READY,
        "Governed request and supplier-input contracts were constructed without missing-evidence inference.",
        route_name=route,
        category=category,
        commodity=commodity,
        source_type=source,
        request=request,
        supplier_inputs=suppliers,
        field_provenance=provenance,
        eligibility_evidence=eligibility_evidence,
        capacity_evidence=capacity_evidence,
        warnings=warnings,
        controlled_defaults_used=(),
    )
