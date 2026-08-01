"""Normalized, deterministic calculation-trace contracts."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from decimal import Decimal
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


def _normalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _normalize(v) for k, v in sorted(value.items(), key=lambda item: str(item[0])) if str(k) not in _VOLATILE_KEYS}
    if isinstance(value, (list, tuple)):
        return [_normalize(v) for v in value]
    if isinstance(value, set):
        return sorted(_normalize(v) for v in value)
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            raise ValueError("Non-finite values are not traceable")
        return format(Decimal(str(value)).normalize(), "f")
    if isinstance(value, Decimal):
        return format(value.normalize(), "f")
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    if hasattr(value, "to_dict"):
        return _normalize(value.to_dict())
    return repr(value)


def deterministic_trace_id(identity_payload: dict) -> str:
    normalized = _normalize(identity_payload)
    raw = json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "trace_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


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
    resolved = tuple(asdict(r) for r in resolutions if r.resolved)
    unresolved = tuple(asdict(r) for r in resolutions if not r.resolved)
    steps = tuple(asdict(s) for s in intermediate_steps)
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
        "configuration_versions": configuration_versions or {},
    }
    trace_id = deterministic_trace_id(identity)
    return CalculationTrace(
        TRACE_CONTRACT_VERSION, calculation_id, formula_id, formula_version, category,
        supplier, rfq_scenario, dict(input_snapshot), tuple(r.assumption_id for r in resolutions),
        resolved, unresolved, steps, raw_output, weighted_contribution, threshold_record,
        blocking_rule_record, recommendation_impact, human_review_status,
        timestamp or datetime.now(timezone.utc).isoformat(), trace_id,
    )
