"""Business-readable Trace and Reconciliation presentation for the Explorer."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import pandas as pd
import streamlit as st


def _humanize(value: Any) -> str:
    text = str(value or "Not available")
    return text.replace("_", " ").strip().title()


def _summary_rows(payload: Mapping[str, Any] | None) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for key, value in (payload or {}).items():
        if isinstance(value, Mapping):
            display = f"{len(value)} registered field(s)"
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            display = f"{len(value)} item(s)"
        elif value is None or value == "":
            display = "Not available"
        else:
            display = str(value)
        rows.append({"Field": _humanize(key), "Value": display})
    return rows


def prepare_trace_presentation(trace: Mapping[str, Any]) -> dict[str, Any]:
    """Prepare readable trace summaries without changing the governed payload."""
    raw_output = trace.get("raw_output")
    input_snapshot = trace.get("input_snapshot") or {}
    intermediate_steps = trace.get("intermediate_steps") or ()
    unresolved = trace.get("unresolved_or_rejected_parameters") or ()
    return {
        "input_rows": _summary_rows(input_snapshot),
        "output_rows": _summary_rows(raw_output if isinstance(raw_output, Mapping) else {}),
        "intermediate_count": len(intermediate_steps),
        "unresolved_count": len(unresolved),
        "decision_impact": {
            "Blocking rule": trace.get("blocking_rule_record") or "None recorded",
            "Recommendation impact": trace.get("recommendation_impact") or "No direct impact recorded",
            "Configuration evidence": trace.get("configuration_versions_status") or "Not available",
        },
        "technical_payload": {
            "input_snapshot": input_snapshot,
            "raw_output": raw_output,
            "intermediate_steps": intermediate_steps,
            "unresolved_or_rejected_parameters": unresolved,
            "blocking_rule_record": trace.get("blocking_rule_record"),
            "recommendation_impact": trace.get("recommendation_impact"),
            "configuration_versions": trace.get("configuration_versions"),
        },
    }


def prepare_reconciliation_presentation(item: Mapping[str, Any]) -> dict[str, Any]:
    """Prepare readable reconciliation evidence while retaining exact technical lists."""
    exact = item.get("exact_matches") or ()
    tolerated = item.get("tolerated_differences") or ()
    mismatches = item.get("mismatches") or ()
    unavailable = item.get("unavailable_evidence") or ()
    tolerance_rules = item.get("tolerance_rules") or ()
    rows = [
        {"Evidence class": "Exact matches", "Count": len(exact), "Review meaning": "Authoritative and compared evidence align."},
        {"Evidence class": "Tolerated differences", "Count": len(tolerated), "Review meaning": "Difference is within an approved tolerance rule."},
        {"Evidence class": "Mismatches", "Count": len(mismatches), "Review meaning": "Potential inconsistency requiring review."},
        {"Evidence class": "Unavailable evidence", "Count": len(unavailable), "Review meaning": "Evidence was not available and was not fabricated."},
    ]
    return {
        "rows": rows,
        "review_required": bool(mismatches or unavailable),
        "technical_payload": {
            "exact_matches": exact,
            "tolerated_differences": tolerated,
            "mismatches": mismatches,
            "unavailable_evidence": unavailable,
            "tolerance_rules": tolerance_rules,
        },
    }


def render_readable_trace(presentation: Mapping[str, Any]) -> None:
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

    prepared = prepare_trace_presentation(trace)
    st.subheader("Input summary")
    if prepared["input_rows"]:
        st.dataframe(pd.DataFrame(prepared["input_rows"]), use_container_width=True, hide_index=True)
    else:
        st.info("No governed input snapshot is available.")

    st.subheader("Authoritative output summary")
    if prepared["output_rows"]:
        st.dataframe(pd.DataFrame(prepared["output_rows"]), use_container_width=True, hide_index=True)
    else:
        st.info("No structured authoritative output is available for summary presentation.")

    counts = st.columns(2)
    counts[0].metric("Intermediate steps", prepared["intermediate_count"])
    counts[1].metric("Unresolved parameters", prepared["unresolved_count"])

    st.subheader("Governed decision impact")
    st.dataframe(
        pd.DataFrame([{"Control": key, "Status": value} for key, value in prepared["decision_impact"].items()]),
        use_container_width=True,
        hide_index=True,
    )

    with st.expander("Technical trace evidence", expanded=False):
        st.json(prepared["technical_payload"])
        st.caption("Exact governed trace payload retained for technical audit. The readable summary does not replace trace authority.")


def render_readable_reconciliation(presentation: Mapping[str, Any]) -> None:
    item = presentation["reconciliation_summary"]
    classification = str(item.get("classification"))
    blocking_status = str(item.get("blocking_status"))
    if blocking_status == "blocked":
        st.error(f"{classification} — blocked")
    elif blocking_status == "review_required":
        st.warning(f"{classification} — human review required")
    else:
        st.success(f"{classification} — evidence aligned; human approval still required")

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

    prepared = prepare_reconciliation_presentation(item)
    st.subheader("Evidence assessment")
    st.dataframe(pd.DataFrame(prepared["rows"]), use_container_width=True, hide_index=True)
    if prepared["review_required"]:
        st.warning("Mismatch or unavailable evidence exists. Human review is required before relying on this reconciliation.")
    else:
        st.caption("No mismatch or unavailable-evidence condition is present in this reconciliation record.")

    with st.expander("Technical reconciliation evidence", expanded=False):
        st.json(prepared["technical_payload"])
        st.caption("Exact reconciliation arrays retained for technical audit. The readable assessment does not change classification authority.")
