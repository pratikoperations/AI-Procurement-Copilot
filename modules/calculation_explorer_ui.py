"""Streamlit rendering for the read-only Governed Calculation Explorer."""
from __future__ import annotations

from collections.abc import Mapping as MappingABC
from typing import Any, Mapping

import pandas as pd
import streamlit as st

SECTIONS = ("Overview", "Assumptions", "Calculation Trace", "Reconciliation", "SourceMate", "Human Review")

_PRINCIPAL_RESULT_KEYS = (
    "target_unit_cost_usd",
    "target_unit_cost_inr",
    "target_unit_cost",
    "risk_adjusted_tco",
    "adjusted_tco",
    "total_cost",
    "annual_cost",
    "score",
    "result",
)

_RESULT_LABELS = {
    "target_unit_cost_usd": "Target Unit Cost",
    "target_unit_cost_inr": "Target Unit Cost",
    "target_unit_cost": "Target Unit Cost",
    "risk_adjusted_tco": "Risk-Adjusted TCO",
    "adjusted_tco": "Adjusted TCO",
    "total_cost": "Total Cost",
    "annual_cost": "Annual Cost",
    "commodity_index": "Commodity Index",
    "conversion_premium": "Conversion Premium",
    "quality_premium": "Quality Premium",
    "supplier_margin": "Supplier Margin",
}

_RESULT_METADATA_KEYS = {"unit", "currency", "uom", "principal_result_key"}


def _humanize_result_field(key: str) -> str:
    """Return a stable procurement-readable label without changing the source key."""
    if key in _RESULT_LABELS:
        return _RESULT_LABELS[key]
    return key.replace("_", " ").strip().title() or "Result"


def _format_result_value(value: Any) -> str:
    """Apply presentation-only precision while preserving the authoritative payload."""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, float):
        if abs(value) >= 100:
            return f"{value:,.2f}"
        if abs(value) >= 10:
            return f"{value:,.3f}".rstrip("0").rstrip(".")
        return f"{value:,.4f}".rstrip("0").rstrip(".")
    if value is None:
        return "Not available"
    return str(value)


def _result_unit(item: Mapping[str, Any], result: Any) -> str:
    if isinstance(result, MappingABC):
        embedded = result.get("unit") or result.get("uom")
        if embedded:
            return str(embedded)
    return str(item.get("unit") or "").strip()


def _find_principal_result_key(item: Mapping[str, Any], result: Mapping[str, Any]) -> str | None:
    explicit = item.get("principal_result_key") or result.get("principal_result_key")
    if explicit and explicit in result and not isinstance(result[explicit], MappingABC):
        return str(explicit)
    for key in _PRINCIPAL_RESULT_KEYS:
        if key in result and result[key] is not None and not isinstance(result[key], MappingABC):
            return key
    for key, value in result.items():
        if key not in _RESULT_METADATA_KEYS and isinstance(value, (int, float)) and not isinstance(value, bool):
            return str(key)
    return None


def _component_unit(key: str, overall_unit: str) -> str:
    if key in {"commodity", "category", "supplier", "scenario"}:
        return ""
    if key.endswith("_index") or key == "commodity_index":
        return "Index"
    return overall_unit


def _component_rows(result: Mapping[str, Any], principal_key: str | None, overall_unit: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key, value in result.items():
        if key in _RESULT_METADATA_KEYS or key == principal_key:
            continue
        if isinstance(value, MappingABC):
            for nested_key, nested_value in value.items():
                rows.append({
                    "Component": _humanize_result_field(str(nested_key)),
                    "Value": _format_result_value(nested_value),
                    "Unit": _component_unit(str(nested_key), overall_unit),
                })
            continue
        rows.append({
            "Component": _humanize_result_field(str(key)),
            "Value": _format_result_value(value),
            "Unit": _component_unit(str(key), overall_unit),
        })
    return rows


def _prepare_result_presentation(item: Mapping[str, Any]) -> dict[str, Any]:
    """Build a presentation-only view of an authoritative calculation result."""
    result = item.get("result")
    unit = _result_unit(item, result)
    if result is None or result == "" or result == {}:
        return {"status": "unavailable", "technical_payload": result}
    if not isinstance(result, MappingABC):
        return {
            "status": "scalar",
            "principal": {"label": "Result", "value": _format_result_value(result), "unit": unit},
            "components": [],
            "technical_payload": result,
        }

    principal_key = _find_principal_result_key(item, result)
    principal = None
    if principal_key is not None:
        principal = {
            "key": principal_key,
            "label": _humanize_result_field(principal_key),
            "value": _format_result_value(result.get(principal_key)),
            "unit": unit,
        }
    return {
        "status": "mapping",
        "principal": principal,
        "components": _component_rows(result, principal_key, unit),
        "technical_payload": result,
    }


def _status_message(classification: str, blocking_status: str) -> None:
    if blocking_status == "blocked":
        st.error(f"{classification} — blocked")
    elif blocking_status == "review_required":
        st.warning(f"{classification} — human review required")
    else:
        st.success(f"{classification} — evidence aligned; human approval still required")


def _render_result(item: Mapping[str, Any]) -> None:
    prepared = _prepare_result_presentation(item)
    if prepared["status"] == "unavailable":
        st.info("Calculation result not available. No value has been fabricated.")
        return

    principal = prepared.get("principal")
    if principal:
        display_value = principal["value"]
        if principal.get("unit"):
            display_value = f"{display_value} {principal['unit']}"
        st.metric(principal["label"], display_value)

    components = prepared.get("components") or []
    if components:
        st.write("**Calculation components**")
        st.dataframe(pd.DataFrame(components), use_container_width=True, hide_index=True)

    with st.expander("Technical result payload", expanded=False):
        st.json(prepared["technical_payload"])
        st.caption("Authoritative payload retained for technical audit. The values are not recalculated by the Explorer.")


def _render_overview(presentation: Mapping[str, Any]) -> None:
    item = presentation["calculation_overview"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Calculation", item.get("calculation_id") or "Not available")
    c2.metric("Formula", f"{item.get('formula_id')} v{item.get('formula_version')}")
    c3.metric("Category", item.get("category") or "Not available")
    c4.metric("Status", item.get("status") or "Not available")
    st.write(f"**Business name:** {item.get('business_name')}")
    st.write(f"**Authoritative source:** `{item.get('source_module')}::{item.get('source_function')}`")
    _render_result(item)
    st.write(f"**Owner:** {item.get('owner')}")
    st.write("**Downstream outputs:** " + ", ".join(item.get("downstream_outputs") or ("None registered",)))
    with st.expander("Formula documentation — non-executable", expanded=False):
        st.code(str(item.get("formula_text") or "No documented expression"), language=None)
        st.caption("Formula metadata is documentation only. The Explorer never evaluates it.")


def _render_assumptions(presentation: Mapping[str, Any]) -> None:
    counts = presentation.get("provenance_counts") or {}
    columns = st.columns(4)
    for column, status in zip(columns, ("supplied", "defaulted", "inferred", "derived")):
        column.metric(status.title(), counts.get(status, 0))
    rows = [{
        "Assumption": item.get("business_name") or item.get("key"),
        "Value": item.get("value"),
        "Unit": item.get("unit"),
        "Provenance": item.get("status"),
        "Source level": item.get("source_level"),
        "Evidence": item.get("evidence_classification"),
        "Source reference": item.get("source_reference"),
        "Effective date": item.get("effective_date"),
        "Review expiry": item.get("review_expiry_date"),
        "Confidence": item.get("confidence"),
        "Override": item.get("override_status"),
        "Approver": item.get("approver"),
        "Governance caveat": item.get("governance_caveat"),
    } for item in presentation.get("assumptions") or ()]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.caption("This register is read-only. Uncatalogued and unavailable evidence remains visible rather than being inferred.")


def _render_trace(presentation: Mapping[str, Any]) -> None:
    trace = presentation["trace_summary"]
    if not trace.get("available"):
        st.warning("A dedicated governed trace adapter is not available for this route. No replacement trace has been fabricated.")
        return
    c1, c2, c3 = st.columns(3)
    c1.metric("Trace ID", trace.get("trace_id") or "Not available")
    c2.metric("Trace contract", trace.get("trace_contract_version") or "Not available")
    c3.metric("Human review", trace.get("human_review_status") or "required")
    st.write(f"**Calculation identity:** {trace.get('calculation_id')} / {trace.get('formula_id')} v{trace.get('formula_version')}")
    st.write(f"**Category:** {trace.get('category')} | **Supplier:** {trace.get('supplier') or 'Not applicable'} | **Scenario:** {trace.get('rfq_scenario') or 'Not applicable'}")
    with st.expander("Input snapshot", expanded=False):
        st.json(trace.get("input_snapshot") or {})
    with st.expander("Authoritative raw output", expanded=False):
        st.json(trace.get("raw_output"))
    with st.expander("Intermediate steps and unavailable parameters", expanded=False):
        st.json({"intermediate_steps": trace.get("intermediate_steps") or (), "unresolved_or_rejected_parameters": trace.get("unresolved_or_rejected_parameters") or ()})
    with st.expander("Governed decision impact", expanded=False):
        st.json({"blocking_rule_record": trace.get("blocking_rule_record"), "recommendation_impact": trace.get("recommendation_impact")})
        if trace.get("configuration_versions_status") == "satisfied":
            st.write("**Configuration versions**")
            st.json(trace.get("configuration_versions"))
        else:
            st.warning(trace.get("configuration_versions_note") or "Configuration-version evidence is unavailable.")


def _render_reconciliation(presentation: Mapping[str, Any]) -> None:
    item = presentation["reconciliation_summary"]
    _status_message(str(item.get("classification")), str(item.get("blocking_status")))
    if not item.get("available"):
        st.info("The authoritative route is available, but dedicated adapter reconciliation is deferred for this route.")
        return
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Exact", len(item.get("exact_matches") or ()))
    c2.metric("Tolerated", len(item.get("tolerated_differences") or ()))
    c3.metric("Mismatches", len(item.get("mismatches") or ()))
    c4.metric("Unavailable", len(item.get("unavailable_evidence") or ()))
    st.write(f"**Reconciliation ID:** `{item.get('reconciliation_id')}`")
    st.write(f"**Authoritative service:** `{item.get('authoritative_service')}`")
    with st.expander("Reconciliation evidence", expanded=False):
        st.json({"exact_matches": item.get("exact_matches") or (), "tolerated_differences": item.get("tolerated_differences") or (), "mismatches": item.get("mismatches") or (), "unavailable_evidence": item.get("unavailable_evidence") or (), "tolerance_rules": item.get("tolerance_rules") or ()})


def _render_sourcemate(presentation: Mapping[str, Any]) -> None:
    item = presentation["sourcemate"]
    st.subheader("SourceMate — Basic Evidence View")
    c1, c2, c3 = st.columns(3)
    c1.metric("Coverage", item.get("coverage_classification"))
    c2.metric("Evidence", item.get("evidence_registration_status"))
    c3.metric("Human review", "Required")
    st.write(f"**Source:** `{item.get('source_module')}::{item.get('source_function')}`")
    st.write(f"**Catalogue reference:** {item.get('calculation_id')} / {item.get('formula_id')} v{item.get('formula_version')}")
    if item.get("dedicated_adapter_deferred"):
        st.warning("Authoritative service available. Dedicated governed adapter deferred. Route is not represented as adapter-reconciled. Human review required.")
    st.dataframe(pd.DataFrame(item.get("export_evidence") or []), use_container_width=True, hide_index=True)
    with st.expander("Assumption evidence references", expanded=False):
        st.dataframe(pd.DataFrame(item.get("assumption_sources") or []), use_container_width=True, hide_index=True)
    for limitation in item.get("limitations") or ():
        st.caption(limitation)


def _render_human_review(presentation: Mapping[str, Any]) -> None:
    st.warning("Read-only checklist. No approval, award, allocation, workflow assignment, or audit writeback is performed.")
    st.dataframe(pd.DataFrame(presentation.get("human_review_checklist") or []), use_container_width=True, hide_index=True)
    st.subheader("Governance disclosures")
    for disclosure in presentation.get("governance_disclosures") or ():
        st.write(f"- {disclosure}")


def render_governed_calculation_explorer(presentation: Mapping[str, Any]) -> None:
    """Render six read-only sections without adding decision controls."""
    st.header("Governed Calculation Explorer")
    st.caption("Read-only explanation of authoritative procurement calculations, assumptions, evidence and review status.")
    status = st.columns(4)
    status[0].info("Authoritative services")
    status[1].info("Formula metadata non-executable")
    status[2].info("Evidence disclosed")
    status[3].info("Human approval mandatory")
    section = st.radio("Explorer section", SECTIONS, horizontal=True, label_visibility="collapsed")
    renderers = {"Overview": _render_overview, "Assumptions": _render_assumptions, "Calculation Trace": _render_trace, "Reconciliation": _render_reconciliation, "SourceMate": _render_sourcemate, "Human Review": _render_human_review}
    renderers[section](presentation)
