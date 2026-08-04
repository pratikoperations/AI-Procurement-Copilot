"""Deterministic, read-only SourceMate conversation service.

Selected-calculation questions use live Governed Calculation Explorer evidence.
Supplier questions use already-produced read-only decision context. Project-wide
questions use the governed repository-derived registry. No calculation, scoring,
recommendation, allocation, approval or procurement action is executed here.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from modules.sourcemate_global_context import GLOSSARY, GLOBAL_CONTEXT_CONTRACT
from modules.sourcemate_project_knowledge import (
    PROJECT_KNOWLEDGE_CONTRACT,
    project_topic_catalogue,
    search_project_knowledge,
)

SOURCEMATE_CONVERSATION_CONTRACT = "AIPC-SOURCEMATE-PROJECT-WIDGET-BIV-1.0"
SUPPORTED_INTENTS = (
    "live_supplier_results",
    "calculation",
    "assumptions",
    "trace",
    "reconciliation",
    "evidence",
    "glossary",
    "project_knowledge",
    "limitations",
    "clarification",
    "unavailable",
)

_EXTERNAL_TERMS = (
    "next month", "next year", "today's price", "today price", "current market price",
    "latest market", "live market", "news", "internet", "external website", "forecast",
    "predict price",
)
_LIVE_RESULT_TERMS = (
    "vendor", "supplier", "qualified", "eligible", "quote", "quoted", "rfq rate",
    "tco adjusted", "tco-adjusted", "score", "rank", "recommended", "recommendation",
)


def _text(value: Any, fallback: str = "Not available in current evidence") -> str:
    if value is None or value == "" or value == () or value == [] or value == {}:
        return fallback
    return str(value)


def _source_refs(*items: str | None) -> list[str]:
    refs: list[str] = []
    for item in items:
        value = str(item or "").strip()
        if value and value not in refs:
            refs.append(value)
    return refs


def _glossary_matches(question: str) -> list[tuple[str, str]]:
    text = str(question or "").lower()
    matches: list[tuple[str, str]] = []
    for term, meaning in GLOSSARY.items():
        normalized = term.lower()
        if normalized in text or text.strip(" ?.!:") == normalized:
            matches.append((term, meaning))
    return matches


def classify_intent(question: str, presentation: Mapping[str, Any] | None = None) -> str:
    """Classify a bounded procurement-project question deterministically."""
    text = str(question or "").strip().lower()
    presentation = presentation or {}
    if not text:
        return "clarification"
    if any(term in text for term in ("can you browse", "browse the web", "can you approve", "approve supplier", "award supplier", "write to erp", "your limitation", "what can you not")):
        return "limitations"
    if any(term in text for term in _EXTERNAL_TERMS):
        return "unavailable"
    if presentation.get("supplier_rows") and any(term in text for term in _LIVE_RESULT_TERMS):
        return "live_supplier_results"
    if any(term in text for term in ("assumption", "selected input", "selected parameter")) and not any(term in text for term in ("tco", "risk", "srm", "scoring", "allocation", "rfq", "project")):
        return "assumptions"
    if any(term in text for term in ("trace", "calculation path", "selected calculation step")):
        return "trace"
    if any(term in text for term in ("reconcile", "reconciliation", "mismatch", "tolerance")):
        return "reconciliation"
    if any(term in text for term in ("selected evidence", "source reference", "selected provenance")):
        return "evidence"
    if any(term in text for term in ("selected calculation", "current result", "current calculation", "target unit cost")):
        return "calculation"
    if search_project_knowledge(text):
        return "project_knowledge"
    if _glossary_matches(text):
        return "glossary"
    if text in {"result", "what is the result", "what is the result?"}:
        return "calculation"
    return "unavailable"


def _answer_live_supplier(question: str, context: Mapping[str, Any]) -> tuple[str, list[str], bool]:
    rows = list(context.get("supplier_rows") or [])
    if not rows:
        return (
            "Verified live context: no approved supplier-result context is available on this page. "
            "SourceMate has not invented a vendor, quote, TCO rate, score, rank or recommendation.",
            list(context.get("evidence_references") or []),
            False,
        )
    q = str(question or "").lower()
    selected = [row for row in rows if str(row.get("supplier") or "").lower() in q]
    if not selected:
        selected = rows
    columns = [
        ("Supplier", "supplier"),
        ("Qualification / eligibility", "eligibility"),
        ("RFQ quote", "quote"),
        ("Quote currency", "quote_currency"),
        ("Normalized rate", "normalized_rate"),
        ("TCO-adjusted rate", "tco_adjusted_rate"),
        ("Score", "score"),
        ("Rank", "rank"),
        ("Risk", "risk"),
        ("Recommendation", "recommendation_status"),
    ]
    requested_keys = {"supplier", "eligibility"}
    if any(term in q for term in ("quote", "quoted", "rfq rate", "rate")):
        requested_keys.update({"quote", "quote_currency", "normalized_rate"})
    if "tco" in q:
        requested_keys.add("tco_adjusted_rate")
    if "score" in q:
        requested_keys.add("score")
    if "rank" in q:
        requested_keys.add("rank")
    if "risk" in q:
        requested_keys.add("risk")
    if any(term in q for term in ("recommend", "selected", "best")):
        requested_keys.add("recommendation_status")
    if len(requested_keys) <= 2:
        requested_keys.update({"quote", "quote_currency", "normalized_rate", "tco_adjusted_rate", "score", "rank", "risk", "recommendation_status"})
    chosen = [(label, key) for label, key in columns if key in requested_keys]
    header = "| " + " | ".join(label for label, _ in chosen) + " |"
    separator = "|" + "|".join("---" for _ in chosen) + "|"
    body: list[str] = []
    missing: set[str] = set()
    for row in selected:
        values: list[str] = []
        for _, key in chosen:
            value = row.get(key)
            if value is None or value == "":
                values.append("Unavailable")
                missing.add(key)
            else:
                values.append(str(value))
        body.append("| " + " | ".join(values) + " |")
    source = "synthetic demonstration data" if context.get("synthetic_demo") else str(context.get("data_source") or "current approved context")
    scope = (
        f"Verified live decision context — category: {_text(context.get('category'))}; material: {_text(context.get('commodity'))}; "
        f"source: {source}; display currency: {_text(context.get('display_currency'))}."
    )
    answer = scope + "\n\n" + "\n".join([header, separator, *body])
    if missing:
        answer += "\n\nUnavailable fields were shown as unavailable rather than inferred: " + ", ".join(sorted(missing)) + "."
    answer += (
        "\n\nEligibility is a hard qualification gate. Score, rank and recommendation are separate governed outputs. "
        "The table reports existing application results; SourceMate did not recalculate or approve them. Human procurement review remains mandatory."
    )
    return answer, list(context.get("evidence_references") or []), True


def _answer_calculation(presentation: Mapping[str, Any]) -> tuple[str, list[str], bool]:
    item = presentation.get("calculation_overview") or {}
    result = item.get("result")
    if result is None or result == "" or result == {}:
        return "Verified evidence: the selected calculation has no available authoritative result. No value has been fabricated.", [], False
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
    answer = (
        f"Verified evidence: {_text(item.get('business_name'), 'Selected calculation')} has an authoritative result of "
        f"{result_text} {_text(item.get('unit'), '')}. The authoritative service is {source}.\n\n"
        "Generated explanation: this is a read-only explanation of the existing result; SourceMate did not execute or recalculate the formula."
    )
    return answer, _source_refs(source, item.get("calculation_id"), item.get("formula_id")), True


def _answer_assumptions(presentation: Mapping[str, Any]) -> tuple[str, list[str], bool]:
    assumptions = presentation.get("assumptions") or ()
    if not assumptions:
        return "Verified evidence: no governed assumptions are available for the selected calculation. No assumptions have been inferred.", [], False
    lines: list[str] = []
    refs: list[str] = []
    for item in list(assumptions)[:12]:
        if not isinstance(item, Mapping):
            continue
        key = _text(item.get("key") or item.get("assumption_id"), "Unnamed assumption")
        value = _text(item.get("effective_value") if item.get("effective_value") is not None else item.get("value"))
        source = _text(item.get("source_reference") or item.get("source_level"))
        lines.append(f"- {key}: {value} — source: {source}")
        refs.extend(_source_refs(item.get("assumption_id"), item.get("source_reference")))
    return "Verified governed assumptions:\n" + "\n".join(lines) + "\n\nOnly registered assumption evidence is listed.", refs, True


def _answer_trace(presentation: Mapping[str, Any]) -> tuple[str, list[str], bool]:
    trace = presentation.get("calculation_trace") or {}
    if not trace or trace.get("available") is False:
        return "Verified evidence: calculation trace is not available for the selected route. SourceMate cannot reconstruct missing trace evidence.", [], False
    answer = (
        f"Verified trace: trace ID {_text(trace.get('trace_id'))}; contract {_text(trace.get('contract_version'))}; "
        f"human review {_text(trace.get('human_review'))}. Intermediate steps: {len(trace.get('intermediate_steps') or ())}; "
        f"unresolved or rejected parameters: {len(trace.get('unresolved_or_rejected_parameters') or ())}."
    )
    return answer, _source_refs(trace.get("trace_id"), trace.get("contract_version")), True


def _answer_reconciliation(presentation: Mapping[str, Any]) -> tuple[str, list[str], bool]:
    item = presentation.get("reconciliation") or {}
    if not item or item.get("available") is False:
        return "Verified evidence: reconciliation is not available for this route. No match status has been inferred.", [], False
    exact = len(item.get("exact_matches") or ())
    tolerated = len(item.get("tolerated_differences") or ())
    mismatches = len(item.get("mismatches") or ())
    unavailable = len(item.get("unavailable_evidence") or ())
    answer = (
        f"Verified reconciliation: {exact} exact match(es), {tolerated} tolerated difference(s), "
        f"{mismatches} mismatch(es), and {unavailable} unavailable evidence item(s). "
        f"Status: {_text(item.get('status') or item.get('classification'))}."
    )
    return answer, _source_refs(item.get("reconciliation_id"), item.get("authoritative_service")), True


def _answer_evidence(presentation: Mapping[str, Any]) -> tuple[str, list[str], bool]:
    sm = presentation.get("sourcemate") or {}
    if not sm:
        return "Verified evidence: the SourceMate evidence summary is unavailable for the selected calculation.", [], False
    exports = sm.get("export_evidence") or ()
    assumptions = sm.get("assumption_sources") or ()
    answer = (
        f"Verified evidence coverage: {_text(sm.get('coverage_classification'))}. Registered export evidence items: {len(exports)}. "
        f"Registered assumption evidence items: {len(assumptions)}. External verification claimed: "
        f"{_text(sm.get('external_verification_claimed'), 'False')}."
    )
    return answer, _source_refs(sm.get("calculation_id"), sm.get("formula_id"), sm.get("coverage_id")), True


def _answer_glossary(question: str) -> tuple[str, list[str], bool]:
    matches = _glossary_matches(question)
    if not matches:
        return "The governed glossary does not contain this term. No definition has been invented.", [], False
    lines = [f"- **{term}**: {meaning}" for term, meaning in matches]
    return "Governed project terminology:\n" + "\n".join(lines), ["modules/sourcemate_global_context.py::GLOSSARY"], True


def _answer_project(question: str) -> tuple[str, list[str], bool]:
    matches = search_project_knowledge(question)
    if not matches:
        return "The repository knowledge registry does not contain enough evidence to answer this question. No answer has been fabricated.", [], False
    sections: list[str] = []
    refs: list[str] = []
    for item in matches:
        sections.append(f"Verified project evidence — {item['topic']}:\n{item['answer']}")
        refs.extend(_source_refs(*item["sources"]))
    return "\n\n".join(sections) + "\n\nThe response summarizes registered repository logic and does not execute it.", refs, True


def _answer_limitations(presentation: Mapping[str, Any]) -> tuple[str, list[str], bool]:
    sm = presentation.get("sourcemate") or {}
    limits = sm.get("limitations") or (
        "No web browsing or external evidence retrieval.",
        "No formula execution, autonomous recommendation, supplier award, production allocation or ERP writeback.",
        "Human procurement approval remains mandatory.",
    )
    return "SourceMate boundaries:\n" + "\n".join(f"- {item}" for item in limits), _source_refs(sm.get("contract_version"), PROJECT_KNOWLEDGE_CONTRACT), True


def answer_question(question: str, presentation: Mapping[str, Any]) -> dict[str, Any]:
    """Return one evidence-labelled, project-grounded response."""
    intent = classify_intent(question, presentation)
    if intent == "live_supplier_results":
        answer, refs, available = _answer_live_supplier(question, presentation)
    elif intent == "calculation":
        answer, refs, available = _answer_calculation(presentation)
    elif intent == "assumptions":
        answer, refs, available = _answer_assumptions(presentation)
    elif intent == "trace":
        answer, refs, available = _answer_trace(presentation)
    elif intent == "reconciliation":
        answer, refs, available = _answer_reconciliation(presentation)
    elif intent == "evidence":
        answer, refs, available = _answer_evidence(presentation)
    elif intent == "glossary":
        answer, refs, available = _answer_glossary(question)
    elif intent == "project_knowledge":
        answer, refs, available = _answer_project(question)
    elif intent == "limitations":
        answer, refs, available = _answer_limitations(presentation)
    elif intent == "clarification":
        answer = "Please enter a project-related question. Supported topics include live supplier results, terminology, " + ", ".join(project_topic_catalogue()) + "."
        refs, available = [], False
    else:
        answer = (
            "This question requires information outside the approved repository or current live context. SourceMate did not browse, "
            "forecast, infer an external fact or fabricate an answer. Ask about suppliers, RFQ quotes, TCO, risk, scoring, SRM, "
            "allocation, formulas, abbreviations, evidence or governance."
        )
        refs, available = [], False
    return {
        "contract_version": SOURCEMATE_CONVERSATION_CONTRACT,
        "global_context_contract": GLOBAL_CONTEXT_CONTRACT,
        "knowledge_contract": PROJECT_KNOWLEDGE_CONTRACT,
        "intent": intent,
        "answer": answer,
        "evidence_references": refs,
        "evidence_available": available,
        "generated_explanation": intent not in {"clarification", "unavailable"},
        "human_review_required": True,
        "external_retrieval_used": False,
        "calculation_executed": False,
        "action_executed": False,
    }
