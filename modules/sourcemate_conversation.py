"""Deterministic, read-only conversational SourceMate service.

Responses are grounded only in the current Governed Calculation Explorer
presentation. No external retrieval, formula execution, scoring, allocation or
award authority is provided.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

SOURCEMATE_CONVERSATION_CONTRACT = "AIPC-SOURCEMATE-CONVERSATIONAL-BIV-1.0"
SUPPORTED_INTENTS = (
    "calculation",
    "assumptions",
    "trace",
    "reconciliation",
    "evidence",
    "limitations",
    "help",
)


def _text(value: Any, fallback: str = "Not available in current evidence") -> str:
    if value is None or value == "" or value == () or value == [] or value == {}:
        return fallback
    return str(value)


def classify_intent(question: str) -> str:
    """Classify a bounded procurement-evidence question deterministically."""
    text = str(question or "").strip().lower()
    if any(term in text for term in ("assumption", "input", "parameter", "source level")):
        return "assumptions"
    if any(term in text for term in ("trace", "step", "calculation path", "how calculated")):
        return "trace"
    if any(term in text for term in ("reconcile", "reconciliation", "match", "mismatch", "tolerance")):
        return "reconciliation"
    if any(term in text for term in ("evidence", "coverage", "source", "reference", "provenance", "export")):
        return "evidence"
    if any(term in text for term in ("limit", "cannot", "can you", "web", "external", "rag", "approve")):
        return "limitations"
    if any(term in text for term in ("calculation", "result", "cost", "formula", "value", "unit")):
        return "calculation"
    return "help"


def _source_refs(*items: str | None) -> list[str]:
    refs: list[str] = []
    for item in items:
        value = str(item or "").strip()
        if value and value not in refs:
            refs.append(value)
    return refs


def _answer_calculation(presentation: Mapping[str, Any]) -> tuple[str, list[str], bool]:
    item = presentation.get("calculation_overview") or {}
    result = item.get("result")
    if result is None or result == "" or result == {}:
        return "The selected calculation has no available authoritative result. No value has been fabricated.", [], False
    principal_key = item.get("principal_result_key")
    if isinstance(result, Mapping):
        if not principal_key:
            for candidate in result:
                if str(candidate).startswith(("target_", "total_", "risk_adjusted_", "final_")):
                    principal_key = candidate
                    break
        principal = result.get(principal_key) if principal_key else None
        result_text = _text(principal if principal is not None else result)
    else:
        result_text = _text(result)
    source = f"{_text(item.get('source_module'))}::{_text(item.get('source_function'))}"
    body = (
        f"Verified evidence: {_text(item.get('business_name'), 'Selected calculation')} has an authoritative result of "
        f"{result_text} {_text(item.get('unit'), '')}. The authoritative service is {source}.\n\n"
        "Generated explanation: this is a read-only explanation of the existing result; SourceMate did not execute or recalculate the formula."
    )
    return body, _source_refs(source, item.get("calculation_id"), item.get("formula_id")), True


def _answer_assumptions(presentation: Mapping[str, Any]) -> tuple[str, list[str], bool]:
    assumptions = presentation.get("assumptions") or ()
    if not assumptions:
        return "No governed assumptions are available for the selected calculation. No assumptions have been inferred.", [], False
    lines: list[str] = []
    refs: list[str] = []
    for item in list(assumptions)[:8]:
        if not isinstance(item, Mapping):
            continue
        key = _text(item.get("key") or item.get("assumption_id"), "Unnamed assumption")
        value = _text(item.get("effective_value") or item.get("value"))
        source = _text(item.get("source_reference") or item.get("source_level"))
        lines.append(f"- {key}: {value} — source: {source}")
        refs.extend(_source_refs(item.get("assumption_id"), item.get("source_reference")))
    return "Verified governed assumptions:\n" + "\n".join(lines) + "\n\nGenerated explanation: only registered assumption evidence is listed.", refs, True


def _answer_trace(presentation: Mapping[str, Any]) -> tuple[str, list[str], bool]:
    trace = presentation.get("calculation_trace") or {}
    if not trace or trace.get("available") is False:
        return "Calculation trace is not available for the selected route. SourceMate cannot reconstruct missing trace evidence.", [], False
    body = (
        f"Verified trace: trace ID {_text(trace.get('trace_id'))}; contract {_text(trace.get('contract_version'))}; "
        f"human review {_text(trace.get('human_review'))}. Intermediate steps: "
        f"{len(trace.get('intermediate_steps') or ())}; unresolved or rejected parameters: "
        f"{len(trace.get('unresolved_or_rejected_parameters') or ())}.\n\n"
        "Generated explanation: the trace records the governed path and does not grant award authority."
    )
    return body, _source_refs(trace.get("trace_id"), trace.get("contract_version")), True


def _answer_reconciliation(presentation: Mapping[str, Any]) -> tuple[str, list[str], bool]:
    item = presentation.get("reconciliation") or {}
    if not item or item.get("available") is False:
        return "Reconciliation evidence is not available for this route. No match status has been inferred.", [], False
    exact = len(item.get("exact_matches") or ())
    tolerated = len(item.get("tolerated_differences") or ())
    mismatches = len(item.get("mismatches") or ())
    unavailable = len(item.get("unavailable_evidence") or ())
    body = (
        f"Verified reconciliation: {exact} exact match(es), {tolerated} tolerated difference(s), "
        f"{mismatches} mismatch(es), and {unavailable} unavailable evidence item(s). "
        f"Status: {_text(item.get('status') or item.get('classification'))}.\n\n"
        "Generated explanation: any mismatch or unavailable evidence requires human review; SourceMate does not resolve it autonomously."
    )
    return body, _source_refs(item.get("reconciliation_id"), item.get("authoritative_service")), True


def _answer_evidence(presentation: Mapping[str, Any]) -> tuple[str, list[str], bool]:
    sm = presentation.get("sourcemate") or {}
    if not sm:
        return "SourceMate evidence summary is unavailable for the selected calculation.", [], False
    exports = sm.get("export_evidence") or ()
    assumptions = sm.get("assumption_sources") or ()
    body = (
        f"Verified evidence coverage: {_text(sm.get('coverage_classification'))}. "
        f"Registered export evidence items: {len(exports)}. Registered assumption evidence items: {len(assumptions)}. "
        f"External verification claimed: {_text(sm.get('external_verification_claimed'), 'False')}.\n\n"
        "Generated explanation: repository references demonstrate internal provenance, not independent supplier or market verification."
    )
    refs = _source_refs(sm.get("calculation_id"), sm.get("formula_id"), sm.get("coverage_id"))
    return body, refs, True


def _answer_limitations(presentation: Mapping[str, Any]) -> tuple[str, list[str], bool]:
    sm = presentation.get("sourcemate") or {}
    limits = sm.get("limitations") or (
        "No web browsing or external evidence retrieval.",
        "No formula execution, autonomous recommendation, supplier award, production allocation or ERP writeback.",
        "Human procurement approval remains mandatory.",
    )
    lines = "\n".join(f"- {item}" for item in limits)
    return "SourceMate Conversational Basic boundaries:\n" + lines, _source_refs(sm.get("contract_version")), True


def answer_question(question: str, presentation: Mapping[str, Any]) -> dict[str, Any]:
    """Return one bounded, evidence-labelled conversational response."""
    intent = classify_intent(question)
    handlers = {
        "calculation": _answer_calculation,
        "assumptions": _answer_assumptions,
        "trace": _answer_trace,
        "reconciliation": _answer_reconciliation,
        "evidence": _answer_evidence,
        "limitations": _answer_limitations,
    }
    if intent == "help":
        answer = (
            "Ask about the selected calculation result, assumptions, calculation trace, reconciliation, evidence coverage, "
            "source references, or SourceMate limitations. Questions outside the current governed evidence will fail closed."
        )
        refs: list[str] = []
        available = True
    else:
        answer, refs, available = handlers[intent](presentation)
    return {
        "contract_version": SOURCEMATE_CONVERSATION_CONTRACT,
        "intent": intent,
        "answer": answer,
        "evidence_references": refs,
        "evidence_available": available,
        "generated_explanation": intent != "help",
        "human_review_required": True,
        "external_retrieval_used": False,
        "action_executed": False,
    }
