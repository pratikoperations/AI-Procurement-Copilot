"""Streamlit review surfaces for governed v1.3 workbook and E2 handoff."""
from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from modules.rfq_review_state import ReviewState, warning_disposition

PREVIEW_LABEL = "Governed v1.3 Workbook Review Preview"
PREVIEW_CAPTION = (
    "Controlled workbook intake, normalization, evidence and provenance review. "
    "Analytical handoff is available only for confirmed, fully governed Full Sourcing Review workbooks. "
    "This is not a v1.3 application release, autonomous award process, production deployment or live ERP integration."
)


def _finding_rows(result: Any) -> list[dict[str, Any]]:
    return [{
        "Severity": getattr(finding, "severity", "Information"),
        "Code": getattr(finding, "code", "UNKNOWN"),
        "Message": getattr(finding, "message", str(finding)),
        "Sheet": getattr(finding, "sheet", None),
        "Row": getattr(finding, "row_number", None),
        "Field": getattr(finding, "field_name", None),
        "Source Row ID": getattr(finding, "source_row_id", None),
    } for finding in result.findings]


def render_findings(result: Any) -> None:
    rows = _finding_rows(result)
    if not rows:
        st.success("No governed findings were returned.")
        return
    frame = pd.DataFrame(rows)
    order = {"Fatal": 0, "Blocking": 1, "Warning": 2, "Information": 3}
    frame["_order"] = frame["Severity"].map(order).fillna(4)
    st.dataframe(frame.sort_values(["_order", "Code"]).drop(columns="_order"), use_container_width=True)


def render_mapping_reviews(adapter_result: Any) -> tuple[tuple[str, str, str], ...]:
    pending = [item for item in adapter_result.mapping_reviews if item.requires_confirmation]
    if not pending:
        return ()
    st.subheader("Governed mapping confirmation")
    confirmed: list[tuple[str, str, str]] = []
    for item in pending:
        label = f"{item.sheet}: '{item.source_header}' → {item.canonical_field}"
        checked = st.checkbox(label, value=False, key=f"mapping:{item.sheet}:{item.source_header}:{item.canonical_field}")
        st.caption(f"{item.confidence_class} | {item.reason or 'Explicit confirmation required'}")
        if checked and item.canonical_field:
            confirmed.append((item.sheet, item.source_header, item.canonical_field))
    return tuple(confirmed)


def render_event_selection(adapter_result: Any) -> str | None:
    events = tuple(adapter_result.available_sourcing_event_ids)
    if len(events) <= 1:
        return events[0] if events else None
    options = ["Select one sourcing event", *events]
    selected = st.selectbox("Sourcing event", options, index=0, key="governed_v13_event")
    return None if selected == options[0] else selected


def render_item_selection(orchestration_result: Any) -> tuple[str | None, str | None]:
    keys = sorted({
        (str(item.record.canonical_values.get("RFQ_NUMBER") or ""), str(item.record.canonical_values.get("RFQ_ITEM") or ""))
        for item in orchestration_result.enriched_quotes if item.eligible_for_analysis
    })
    options = ["Select one RFQ item", *[f"{number} | {item}" for number, item in keys]]
    selected = st.selectbox("RFQ item", options, index=0, key="governed_v13_item")
    if selected == options[0]:
        return None, None
    return tuple(selected.split(" | ", 1))


def render_warning_acknowledgements(orchestration_result: Any, mode: str) -> tuple[str, ...]:
    acknowledged: list[str] = []
    for code in orchestration_result.warnings:
        disposition = warning_disposition(code, mode).value
        if disposition == "ACKNOWLEDGEMENT_REQUIRED":
            if st.checkbox(f"Acknowledge {code}", value=False, key=f"warning:{code}"):
                acknowledged.append(code)
        elif disposition == "COMPATIBILITY_BLOCKING":
            st.error(f"{code}: compatibility blocking")
        else:
            st.info(f"{code}: display-only finding")
    return tuple(acknowledged)


def render_normalized_preview(orchestration_result: Any) -> None:
    rows: list[dict[str, Any]] = []
    for item in orchestration_result.enriched_quotes:
        values = item.record.canonical_values
        normalized = item.normalization.normalized_values
        rows.append({
            "RFQ Number": values.get("RFQ_NUMBER"),
            "RFQ Item": values.get("RFQ_ITEM"),
            "Supplier ID": values.get("SUPPLIER_ID"),
            "Supplier Name": values.get("SUPPLIER_NAME"),
            "Source Currency": normalized.get("SOURCE_CURRENCY"),
            "Source Price": normalized.get("SOURCE_PRICE"),
            "Workbook Comparison Currency": normalized.get("COMPARISON_CURRENCY"),
            "Normalized Review Unit Price": normalized.get("NORMALIZED_UNIT_PRICE"),
            "Comparison UOM": normalized.get("COMPARISON_UOM"),
            "Eligible for review": item.eligible_for_analysis,
            "Source Row ID": item.record.provenance.source_row_id,
        })
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True)


def render_compatibility(result: Any) -> None:
    compatibility = result.compatibility_result
    if compatibility is None:
        return
    st.subheader("Analytical compatibility")
    for blocker in compatibility.blockers:
        st.error(blocker)
    manifest = pd.DataFrame([item.__dict__ for item in compatibility.manifest])
    if not manifest.empty:
        st.dataframe(manifest, use_container_width=True)


def render_handoff_confirmation(result: Any) -> bool:
    handoff = result.handoff_result
    if result.review_state is not ReviewState.READY_FOR_HANDOFF or handoff is None or not handoff.digest or handoff.manifest is None:
        return False
    st.subheader("Governed analytical handoff")
    st.write(f"**Selected RFQ:** {handoff.manifest.selected_rfq_number} | {handoff.manifest.selected_rfq_item}")
    st.write(f"**Suppliers:** {len(handoff.manifest.suppliers)}")
    st.write(f"**Analytical basis:** {handoff.manifest.analytical_currency} / {handoff.manifest.comparison_uom}")
    st.code(handoff.digest)
    st.caption("The digest binds the upload, selected item, supplier set, canonical ranking evidence, commercial inputs and analytical assumptions.")
    confirmed = st.checkbox(
        "I confirm analytical handoff for this exact RFQ item, supplier set, canonical ranking evidence and USD comparison basis.",
        value=False,
        key="governed_v13_handoff_ack",
    )
    return bool(confirmed and st.button("Confirm governed analytical handoff", type="primary"))


def render_governed_review(result: Any) -> None:
    st.header(PREVIEW_LABEL)
    st.caption(PREVIEW_CAPTION)
    st.write(f"**Review state:** {result.review_state.value}")
    if result.route_warning:
        st.warning(result.route_warning)
    if result.stop_reason:
        if result.review_state in {ReviewState.ADAPTER_FATAL, ReviewState.ORCHESTRATION_BLOCKED, ReviewState.ANALYSIS_INCOMPATIBLE}:
            st.error(result.stop_reason)
        else:
            st.warning(result.stop_reason)
    render_findings(result)
    if result.orchestration_result is not None:
        st.metric("Evidence coverage", f"{result.orchestration_result.event_coverage_percent}%")
        st.caption(f"Aggregation: {result.orchestration_result.event_aggregation_method}")
        render_normalized_preview(result.orchestration_result)
    render_compatibility(result)
    if result.review_state is ReviewState.REVIEW_ONLY_COMPLETE:
        st.info("Governed review is complete. Analytical handoff remains disabled for this route or workbook.")
    elif result.review_state is ReviewState.HANDOFF_CONFIRMED:
        st.success("Governed analytical handoff confirmed for the displayed digest.")
