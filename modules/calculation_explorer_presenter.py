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
        return {
            "available": False,
            "configuration_versions": None,
            "configuration_versions_status": "not_available",
            "configuration_versions_note": "No governed trace is available for this route.",
            "human_review_status": "required",
        }
    trace = deepcopy(dict(trace))
    versions = trace.get("configuration_versions")
    versions_available = isinstance(versions, Mapping) and bool(versions)
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
        "configuration_versions": deepcopy(dict(versions)) if versions_available else None,
        "configuration_versions_status": "satisfied" if versions_available else "not_available",
        "configuration_versions_note": (
            "Governed configuration versions retained by the trace."
            if versions_available
            else "Configuration-version evidence is unavailable in this trace."
        ),
        "human_review_status": trace.get("human_review_status", "required"),
    }


def _reconciliation_summary(reconciliation: Mapping[str, Any] | None) -> dict[str, Any]:
    if reconciliation is None:
        return {
            "available": False,
            "classification": "unsupported_deferred_coverage",
            "blocking_status": "review_required",
            "human_review_status": "required",
        }
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


def _checklist_item(control: str, status: str, note: str) -> dict[str, Any]:
    if status not in {"satisfied", "not_satisfied", "not_available"}:
        raise ValueError(f"Unsupported checklist status: {status}")
    return {
        "control": control,
        "status": status,
        "satisfied": status == "satisfied",
        "note": note,
    }


def _review_checklist(
    *,
    trace_summary: Mapping[str, Any],
    reconciliation_summary: Mapping[str, Any],
    sourcemate: Mapping[str, Any],
    autonomous_award: bool,
    human_review_required: bool,
) -> list[dict[str, Any]]:
    assumption_sources = sourcemate.get("assumption_sources") or ()
    export_evidence = sourcemate.get("export_evidence") or ()
    trace_available = bool(trace_summary.get("available"))
    deferred = bool(sourcemate.get("dedicated_adapter_deferred"))
    reconciliation_classification = reconciliation_summary.get("classification")
    unavailable_evidence = reconciliation_summary.get("unavailable_evidence") or ()
    unresolved_parameters = trace_summary.get("unresolved_or_rejected_parameters") or ()
    unavailable_disclosed = bool(unavailable_evidence or unresolved_parameters)
    trace_human_review = trace_summary.get("human_review_status") == "required"
    reconciliation_human_review = reconciliation_summary.get("human_review_status") == "required"
    sourcemate_human_review = sourcemate.get("human_review_required") is True

    return [
        _checklist_item(
            "Authoritative service identified",
            "satisfied" if sourcemate.get("source_function") else "not_satisfied",
            "Source function is present." if sourcemate.get("source_function") else "Source function is missing.",
        ),
        _checklist_item(
            "Calculation and formula version identified",
            "satisfied" if sourcemate.get("calculation_id") and sourcemate.get("formula_version") else "not_satisfied",
            "Calculation and formula version are present." if sourcemate.get("calculation_id") and sourcemate.get("formula_version") else "Calculation or formula version is missing.",
        ),
        _checklist_item(
            "Assumptions and provenance disclosed",
            "satisfied" if assumption_sources else "not_available",
            f"{len(assumption_sources)} assumption record(s) disclosed." if assumption_sources else "No assumption records are available for this presentation.",
        ),
        _checklist_item(
            "Trace status disclosed",
            "satisfied" if trace_available or deferred else "not_available",
            "Governed trace is available." if trace_available else "Dedicated trace adapter is explicitly deferred." if deferred else "Trace status is unavailable.",
        ),
        _checklist_item(
            "Reconciliation or deferred status disclosed",
            "satisfied" if reconciliation_classification else "not_available",
            f"Classification: {reconciliation_classification}." if reconciliation_classification else "No reconciliation or deferred classification is available.",
        ),
        _checklist_item(
            "Evidence locations disclosed",
            "satisfied" if export_evidence else "not_available",
            f"{len(export_evidence)} registered export-evidence location(s) disclosed." if export_evidence else "No registered export-evidence location exists for this calculation.",
        ),
        _checklist_item(
            "Unavailable evidence not reconstructed",
            "satisfied" if unavailable_disclosed else "not_available",
            "Unavailable or unresolved evidence is explicitly disclosed without reconstruction." if unavailable_disclosed else "No unavailable or unresolved evidence is present in this record.",
        ),
        _checklist_item(
            "Recommendation remains advisory",
            "satisfied" if autonomous_award is False else "not_satisfied",
            "The presentation contract prohibits autonomous award." if autonomous_award is False else "Autonomous-award protection is not active.",
        ),
        _checklist_item(
            "Human approval required",
            "satisfied" if human_review_required and sourcemate_human_review and (trace_human_review or deferred) and reconciliation_human_review else "not_satisfied",
            "Human review is required by the presentation, SourceMate, and available trace/reconciliation evidence." if human_review_required and sourcemate_human_review and (trace_human_review or deferred) and reconciliation_human_review else "Human-review requirements are inconsistent or missing.",
        ),
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
    autonomous_award = False
    human_review_required = True
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
            autonomous_award=autonomous_award,
            human_review_required=human_review_required,
        ),
        "governance_disclosures": list(GOVERNANCE_DISCLOSURES),
        "read_only": True,
        "approval_persistence": False,
        "autonomous_award": autonomous_award,
        "human_review_required": human_review_required,
    }
