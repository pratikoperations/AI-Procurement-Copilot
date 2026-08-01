"""Stable read-only presentation contract for the Governed Calculation Explorer."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping

from modules.sourcemate_presenter import build_sourcemate_summary

EXPLORER_PRESENTATION_CONTRACT_VERSION = "AIPC-GOVERNED-EXPLORER-1.0"
GOVERNANCE_DISCLOSURES = (
    "Formula metadata is documentation only and is never executed.",
    "Existing authoritative procurement services produce business results.",
    "Evidence references do not prove external verification or realized business outcomes.",
    "Unavailable evidence is disclosed and is never reconstructed.",
    "No autonomous award or production allocation is performed.",
    "Human approval remains mandatory.",
)


def _record(value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, Mapping):
        return deepcopy(dict(value))
    raise TypeError(f"Expected dataclass or mapping, received {type(value).__name__}")


def _calculation_overview(calculation: Mapping[str, Any]) -> dict[str, Any]:
    item = deepcopy(dict(calculation))
    return {
        "calculation_id": item.get("calculation_id"),
        "business_name": item.get("business_name"),
        "formula_id": item.get("formula_id"),
        "formula_version": item.get("formula_version"),
        "category": item.get("category"),
        "source_module": item.get("source_module"),
        "source_function": item.get("source_function"),
        "result": deepcopy(item.get("result")),
        "unit": item.get("unit"),
        "owner": item.get("owner"),
        "status": item.get("status"),
        "downstream_outputs": list(item.get("downstream_outputs") or ()),
        "formula_text": item.get("formula_text"),
        "formula_executable": False,
        "governance_caveat": item.get("governance_caveat"),
    }


def _trace_summary(trace: Mapping[str, Any] | None) -> dict[str, Any]:
    if trace is None:
        return {"available": False, "human_review_status": "required"}
    trace = deepcopy(dict(trace))
    return {
        "available": True,
        "trace_id": trace.get("trace_id"),
        "trace_contract_version": trace.get("trace_contract_version"),
        "calculation_id": trace.get("calculation_id"),
        "formula_id": trace.get("formula_id"),
        "formula_version": trace.get("formula_version"),
        "category": trace.get("category"),
        "supplier": trace.get("supplier"),
        "rfq_scenario": trace.get("rfq_scenario"),
        "input_snapshot": deepcopy(trace.get("input_snapshot")),
        "raw_output": deepcopy(trace.get("raw_output")),
        "intermediate_steps": deepcopy(trace.get("intermediate_steps") or ()),
        "unresolved_or_rejected_parameters": deepcopy(trace.get("unresolved_or_rejected_parameters") or ()),
        "blocking_rule_record": deepcopy(trace.get("blocking_rule_record")),
        "recommendation_impact": trace.get("recommendation_impact"),
        "configuration_versions": deepcopy(trace.get("configuration_versions") or {}),
        "human_review_status": trace.get("human_review_status", "required"),
    }


def _reconciliation_summary(reconciliation: Mapping[str, Any] | None) -> dict[str, Any]:
    if reconciliation is None:
        return {"available": False, "classification": "unsupported_deferred_coverage", "blocking_status": "review_required", "human_review_status": "required"}
    reconciliation = deepcopy(dict(reconciliation))
    return {
        "available": True,
        "reconciliation_id": reconciliation.get("reconciliation_id"),
        "contract_version": reconciliation.get("contract_version"),
        "classification": reconciliation.get("classification"),
        "blocking_status": reconciliation.get("blocking_status"),
        "authoritative_service": reconciliation.get("authoritative_service"),
        "exact_matches": deepcopy(reconciliation.get("exact_matches") or ()),
        "tolerated_differences": deepcopy(reconciliation.get("tolerated_differences") or ()),
        "mismatches": deepcopy(reconciliation.get("mismatches") or ()),
        "unavailable_evidence": deepcopy(reconciliation.get("unavailable_evidence") or ()),
        "tolerance_rules": deepcopy(reconciliation.get("tolerance_rules") or ()),
        "human_review_status": reconciliation.get("human_review_status", "required"),
    }


def _review_checklist(*, trace_summary: Mapping[str, Any], reconciliation_summary: Mapping[str, Any], sourcemate: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {"control": "Authoritative service identified", "satisfied": bool(sourcemate.get("source_function"))},
        {"control": "Calculation and formula version identified", "satisfied": bool(sourcemate.get("calculation_id") and sourcemate.get("formula_version"))},
        {"control": "Assumptions and provenance disclosed", "satisfied": True},
        {"control": "Trace status disclosed", "satisfied": bool(trace_summary.get("available")) or sourcemate.get("dedicated_adapter_deferred", False)},
        {"control": "Reconciliation or deferred status disclosed", "satisfied": bool(reconciliation_summary.get("classification"))},
        {"control": "Evidence locations disclosed", "satisfied": True},
        {"control": "Unavailable evidence not reconstructed", "satisfied": True},
        {"control": "Recommendation remains advisory", "satisfied": True},
        {"control": "Human approval required", "satisfied": True},
    ]


def build_governed_explorer_presentation(
    *,
    explorer_payload: Mapping[str, Any],
    calculation_id: str,
    coverage_id: str,
    trace: Any = None,
    reconciliation: Any = None,
    runtime_evidence: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Assemble one immutable UI payload from existing governed contracts."""
    payload = deepcopy(dict(explorer_payload))
    calculation = next((item for item in payload.get("calculations", ()) if item.get("calculation_id") == calculation_id), None)
    if calculation is None:
        raise KeyError(calculation_id)
    assumptions = deepcopy(payload.get("assumptions") or [])
    trace_record = _record(trace)
    reconciliation_record = _record(reconciliation)
    trace_summary = _trace_summary(trace_record)
    reconciliation_summary = _reconciliation_summary(reconciliation_record)
    sourcemate = build_sourcemate_summary(
        calculation=calculation,
        assumptions=assumptions,
        coverage_id=coverage_id,
        runtime_evidence=runtime_evidence,
    )
    return {
        "contract_version": EXPLORER_PRESENTATION_CONTRACT_VERSION,
        "context": deepcopy(payload.get("context") or {}),
        "calculation_overview": _calculation_overview(calculation),
        "assumptions": assumptions,
        "provenance_counts": deepcopy(payload.get("provenance_counts") or {}),
        "trace_summary": trace_summary,
        "reconciliation_summary": reconciliation_summary,
        "sourcemate": sourcemate,
        "human_review_checklist": _review_checklist(
            trace_summary=trace_summary,
            reconciliation_summary=reconciliation_summary,
            sourcemate=sourcemate,
        ),
        "governance_disclosures": list(GOVERNANCE_DISCLOSURES),
        "read_only": True,
        "approval_persistence": False,
        "autonomous_award": False,
        "human_review_required": True,
    }
