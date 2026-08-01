"""Normalized, deterministic calculation-trace contracts."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
from typing import Any

from modules.parameter_precedence import ParameterResolutionResult

TRACE_CONTRACT_VERSION = "AIPC-CALC-TRACE-1.0"
_VOLATILE_KEYS = {"timestamp", "display_timestamp", "rendered_at", "trace_id"}


@dataclass(frozen=True)
class IntermediateStep:
    name: str
    value: Any = None
    unit: str | None = None
    available: bool = True
    source: str = "authoritative_engine"
    note: str | None = None


@dataclass(frozen=True)
class CalculationTrace:
    trace_contract_version: str
    calculation_id: str
    formula_id: str
    formula_version: str
    category: str
    supplier: str | None
    rfq_scenario: str | None
    input_snapshot: dict
    assumption_ids: tuple[str, ...]
    resolved_parameters: tuple[dict, ...]
    unresolved_or_rejected_parameters: tuple[dict, ...]
    intermediate_steps: tuple[dict, ...]
    raw_output: Any
    weighted_contribution: dict | None
    threshold_record: dict | None
    blocking_rule_record: dict | None
    recommendation_impact: str | None
    human_review_status: str
    timestamp: str
    trace_id: str
    configuration_versions: dict = field(default_factory=dict)


def _canonical_number(value: int | float | Decimal) -> dict[str, str]:
    if isinstance(value, bool):
        raise TypeError("Boolean values must not be normalized as numbers")
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"Invalid numeric trace value: {value}") from exc
    if not decimal_value.is_finite():
        raise ValueError("Non-finite values are not traceable")
    if decimal_value == 0:
        decimal_value = Decimal(0)
    normalized = decimal_value.normalize()
    return {"__number__": format(normalized, "f")}


def _normalize_mapping(value: Mapping) -> dict[str, Any]:
    non_string_keys = [key for key in value if not isinstance(key, str)]
    if non_string_keys:
        key_types = ", ".join(
            sorted({type(key).__name__ for key in non_string_keys})
        )
        raise TypeError(
            "Trace mappings require string keys; unsupported key type(s): "
            + key_types
        )

    normalized: dict[str, Any] = {}
    for key in sorted(value):
        if key in _VOLATILE_KEYS:
            continue
        if key in normalized:
            raise ValueError(f"Duplicate normalized trace mapping key: {key}")
        normalized[key] = _normalize(value[key])
    return normalized


def _normalize(value: Any) -> Any:
    if isinstance(value, Mapping):
        return _normalize_mapping(value)
    if isinstance(value, (list, tuple)):
        return [_normalize(item) for item in value]
    if isinstance(value, set):
        normalized_items = [_normalize(item) for item in value]
        return sorted(
            normalized_items,
            key=lambda item: json.dumps(
                item, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            ),
        )
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float, Decimal)):
        return _canonical_number(value)
    if isinstance(value, datetime):
        normalized = value
        if normalized.tzinfo is None:
            normalized = normalized.replace(tzinfo=timezone.utc)
        normalized = normalized.astimezone(timezone.utc)
        return {"__datetime__": normalized.isoformat()}
    if isinstance(value, date):
        return {"__date__": value.isoformat()}
    if isinstance(value, str) or value is None:
        return value
    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        governed = to_dict()
        if not isinstance(governed, Mapping):
            raise TypeError("Governed to_dict() output must be a mapping")
        return _normalize_mapping(governed)
    raise TypeError(f"Unsupported non-deterministic trace value type: {type(value).__name__}")


def deterministic_trace_id(identity_payload: dict) -> str:
    normalized = _normalize(identity_payload)
    raw = json.dumps(
        normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return "trace_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _resolution_sort_key(result: ParameterResolutionResult) -> tuple:
    return (
        result.assumption_id,
        result.selected_source_level or "",
        result.selected_source_record_id or "",
        result.version or "",
        "0" if result.resolved else "1",
    )


def build_trace(
    *,
    calculation_id: str,
    formula_id: str,
    formula_version: str,
    category: str,
    input_snapshot: dict,
    raw_output: Any,
    supplier: str | None = None,
    rfq_scenario: str | None = None,
    resolutions: tuple[ParameterResolutionResult, ...] = (),
    intermediate_steps: tuple[IntermediateStep, ...] = (),
    weighted_contribution: dict | None = None,
    threshold_record: dict | None = None,
    blocking_rule_record: dict | None = None,
    recommendation_impact: str | None = None,
    human_review_status: str = "required",
    configuration_versions: dict | None = None,
    timestamp: str | None = None,
) -> CalculationTrace:
    if human_review_status != "required":
        raise ValueError("Basic Interview Version traces require human review")

    ordered_resolutions = tuple(sorted(resolutions, key=_resolution_sort_key))
    resolved = tuple(asdict(result) for result in ordered_resolutions if result.resolved)
    unresolved = tuple(
        asdict(result) for result in ordered_resolutions if not result.resolved
    )
    steps = tuple(asdict(step) for step in intermediate_steps)
    governed_configuration_versions = dict(configuration_versions or {})
    identity = {
        "contract": TRACE_CONTRACT_VERSION,
        "calculation_id": calculation_id,
        "formula_id": formula_id,
        "formula_version": formula_version,
        "category": category,
        "supplier": supplier,
        "rfq_scenario": rfq_scenario,
        "input_snapshot": input_snapshot,
        "resolved_parameters": resolved,
        "unresolved_parameters": unresolved,
        "raw_output": raw_output,
        "weighted_contribution": weighted_contribution,
        "threshold_record": threshold_record,
        "blocking_rule_record": blocking_rule_record,
        "recommendation_impact": recommendation_impact,
        "configuration_versions": governed_configuration_versions,
    }
    trace_id = deterministic_trace_id(identity)
    return CalculationTrace(
        TRACE_CONTRACT_VERSION,
        calculation_id,
        formula_id,
        formula_version,
        category,
        supplier,
        rfq_scenario,
        dict(input_snapshot),
        tuple(sorted(result.assumption_id for result in ordered_resolutions)),
        resolved,
        unresolved,
        steps,
        raw_output,
        weighted_contribution,
        threshold_record,
        blocking_rule_record,
        recommendation_impact,
        human_review_status,
        timestamp or datetime.now(timezone.utc).isoformat(),
        trace_id,
        governed_configuration_versions,
    )
