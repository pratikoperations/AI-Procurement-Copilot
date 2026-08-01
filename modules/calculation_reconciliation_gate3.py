"""Read-only Gate 3 reconciliation for authoritative outputs and calculation traces."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import math
from typing import Any, Mapping

from modules.calculation_trace import CalculationTrace

RECONCILIATION_CONTRACT_VERSION = "AIPC-RECON-1.0"
CLASSIFICATIONS = {
    "exact_match",
    "rounding_only_difference",
    "unit_display_difference",
    "unavailable_authoritative_intermediate",
    "adapter_defect",
    "metadata_defect",
    "existing_business_logic_inconsistency",
    "export_path_inconsistency",
    "unsupported_deferred_coverage",
}
_PROHIBITED_TOLERANCE_TOKENS = {
    "calculation_id", "formula_id", "formula_version", "trace_id", "status",
    "eligibility", "blocker", "blocking", "recommendation", "allocation_label",
    "scenario_label", "winner", "winner_state",
}


def _normalised_path(path: str) -> str:
    return path.strip().lower().replace("-", "_").replace(" ", "_")


def _is_prohibited_tolerance_path(path: str) -> bool:
    normalised = _normalised_path(path)
    segments = {segment for segment in normalised.replace("[", ".").replace("]", "").split(".") if segment}
    return any(token in normalised or token in segments for token in _PROHIBITED_TOLERANCE_TOKENS)


@dataclass(frozen=True)
class ToleranceRule:
    rule_id: str
    version: str
    field_path: str
    absolute_tolerance: Decimal = Decimal("0")
    classification: str = "rounding_only_difference"

    def __post_init__(self) -> None:
        if not self.rule_id.strip() or not self.version.strip() or not self.field_path.strip():
            raise ValueError("Tolerance rule ID, version and field path are required")
        if self.classification not in {"rounding_only_difference", "unit_display_difference"}:
            raise ValueError("Tolerance rules may classify only rounding or unit-display differences")
        try:
            tolerance = Decimal(str(self.absolute_tolerance))
        except Exception as exc:
            raise ValueError("Tolerance must be numeric") from exc
        if not math.isfinite(float(tolerance)) or tolerance < 0:
            raise ValueError("Tolerance must be finite and non-negative")
        if _is_prohibited_tolerance_path(self.field_path):
            raise ValueError(f"Tolerance is prohibited for governed field '{self.field_path}'")
        object.__setattr__(self, "absolute_tolerance", tolerance)


@dataclass(frozen=True)
class FieldDifference:
    field_path: str
    authoritative_value: Any
    trace_value: Any
    classification: str
    tolerance_rule_id: str | None = None
    tolerance_rule_version: str | None = None


@dataclass(frozen=True)
class ReconciliationResult:
    reconciliation_id: str
    contract_version: str
    trace_id: str
    calculation_id: str
    formula_id: str
    formula_version: str
    category: str
    supplier: str | None
    rfq_scenario: str | None
    authoritative_service: str
    authoritative_output_snapshot: Any
    trace_output_snapshot: Any
    compared_fields: tuple[str, ...]
    tolerance_rules: tuple[dict, ...]
    exact_matches: tuple[str, ...]
    tolerated_differences: tuple[dict, ...]
    mismatches: tuple[dict, ...]
    unavailable_evidence: tuple[str, ...]
    classification: str
    blocking_status: str
    human_review_status: str
    timestamp: str


def _canonical(value: Any) -> Any:
    return json.loads(json.dumps(value, sort_keys=True, default=str, allow_nan=False))


def _path_lookup(value: Any, path: str) -> tuple[bool, Any]:
    current = value
    if not path:
        return True, current
    for segment in path.split("."):
        if isinstance(current, Mapping) and segment in current:
            current = current[segment]
        elif isinstance(current, (list, tuple)) and segment.isdigit() and int(segment) < len(current):
            current = current[int(segment)]
        else:
            return False, None
    return True, current


def _numeric_difference(a: Any, b: Any) -> Decimal | None:
    if isinstance(a, bool) or isinstance(b, bool):
        return None
    if not isinstance(a, (int, float, Decimal)) or not isinstance(b, (int, float, Decimal)):
        return None
    return abs(Decimal(str(a)) - Decimal(str(b)))


def _reconciliation_id(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return "recon_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _validate_tolerance_rules(rules: tuple[ToleranceRule, ...]) -> dict[str, ToleranceRule]:
    ids: set[str] = set()
    paths: set[str] = set()
    indexed: dict[str, ToleranceRule] = {}
    for rule in rules:
        if rule.rule_id in ids:
            raise ValueError(f"Duplicate tolerance rule ID '{rule.rule_id}'")
        if rule.field_path in paths:
            raise ValueError(f"Duplicate tolerance field path '{rule.field_path}'")
        ids.add(rule.rule_id)
        paths.add(rule.field_path)
        indexed[rule.field_path] = rule
    return indexed


def reconcile_trace(
    *, trace: CalculationTrace, authoritative_service: str, authoritative_output: Any,
    calculation_id: str, formula_id: str, formula_version: str,
    compared_fields: tuple[str, ...] = ("",), tolerance_rules: tuple[ToleranceRule, ...] = (),
    unavailable_evidence: tuple[str, ...] = (), expected_blocking_rule: Any = None,
    expected_recommendation_impact: Any = None, repeated_trace_id: str | None = None,
) -> ReconciliationResult:
    """Compare a trace with existing authoritative results without recalculation."""
    if not authoritative_service.strip():
        raise ValueError("Authoritative service is required")
    if len(set(compared_fields)) != len(compared_fields):
        raise ValueError("Compared fields must be unique")
    exact: list[str] = []
    tolerated: list[dict] = []
    mismatches: list[dict] = []
    rules = _validate_tolerance_rules(tolerance_rules)

    for field, expected, actual in (
        ("calculation_id", calculation_id, trace.calculation_id),
        ("formula_id", formula_id, trace.formula_id),
        ("formula_version", formula_version, trace.formula_version),
    ):
        if expected != actual:
            mismatches.append(asdict(FieldDifference(field, expected, actual, "metadata_defect")))

    for field_path in compared_fields:
        authoritative_present, expected = _path_lookup(authoritative_output, field_path)
        trace_present, actual = _path_lookup(trace.raw_output, field_path)
        if not authoritative_present or not trace_present:
            if not authoritative_present and not trace_present:
                expected_marker, actual_marker = "missing", "missing"
            elif not authoritative_present:
                expected_marker, actual_marker = "missing", "present"
            else:
                expected_marker, actual_marker = "present", "missing"
            mismatches.append(asdict(FieldDifference(field_path, expected_marker, actual_marker, "adapter_defect")))
            continue
        if _canonical(expected) == _canonical(actual):
            exact.append(field_path or "$raw_output")
            continue
        rule = rules.get(field_path)
        difference = _numeric_difference(expected, actual)
        if rule and difference is not None and difference <= rule.absolute_tolerance:
            tolerated.append(asdict(FieldDifference(
                field_path, expected, actual, rule.classification, rule.rule_id, rule.version
            )))
        else:
            mismatches.append(asdict(FieldDifference(field_path, expected, actual, "existing_business_logic_inconsistency")))

    if expected_blocking_rule is not None and _canonical(trace.blocking_rule_record) != _canonical(expected_blocking_rule):
        mismatches.append(asdict(FieldDifference("blocking_rule_record", expected_blocking_rule, trace.blocking_rule_record, "adapter_defect")))
    if expected_recommendation_impact is not None and trace.recommendation_impact != expected_recommendation_impact:
        mismatches.append(asdict(FieldDifference("recommendation_impact", expected_recommendation_impact, trace.recommendation_impact, "adapter_defect")))
    if repeated_trace_id is not None and repeated_trace_id != trace.trace_id:
        mismatches.append(asdict(FieldDifference("trace_id", trace.trace_id, repeated_trace_id, "adapter_defect")))

    if mismatches:
        classification, blocking_status = mismatches[0]["classification"], "blocked"
    elif tolerated:
        classification, blocking_status = tolerated[0]["classification"], "review_required"
    elif unavailable_evidence:
        classification, blocking_status = "unavailable_authoritative_intermediate", "review_required"
    else:
        classification, blocking_status = "exact_match", "clear"

    normalised_rules = tuple(asdict(rule) for rule in tolerance_rules)
    identity = {
        "trace_id": trace.trace_id,
        "calculation_id": calculation_id,
        "formula_id": formula_id,
        "formula_version": formula_version,
        "authoritative_service": authoritative_service,
        "compared_fields": tuple(compared_fields),
        "tolerance_rules": normalised_rules,
        "exact": exact,
        "tolerated": tolerated,
        "mismatches": mismatches,
        "unavailable": tuple(unavailable_evidence),
        "classification": classification,
        "blocking": blocking_status,
    }
    return ReconciliationResult(
        reconciliation_id=_reconciliation_id(identity), contract_version=RECONCILIATION_CONTRACT_VERSION,
        trace_id=trace.trace_id, calculation_id=calculation_id, formula_id=formula_id,
        formula_version=formula_version, category=trace.category, supplier=trace.supplier,
        rfq_scenario=trace.rfq_scenario, authoritative_service=authoritative_service,
        authoritative_output_snapshot=_canonical(authoritative_output), trace_output_snapshot=_canonical(trace.raw_output),
        compared_fields=tuple(compared_fields), tolerance_rules=normalised_rules,
        exact_matches=tuple(exact), tolerated_differences=tuple(tolerated), mismatches=tuple(mismatches),
        unavailable_evidence=tuple(unavailable_evidence), classification=classification,
        blocking_status=blocking_status, human_review_status="required",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
