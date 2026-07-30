"""Streamlit review surfaces for governed v1.3 workbook and E2 handoff."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import pandas as pd
import streamlit as st

from modules.ranking_input_models import RankingMappingConfirmation
from modules.rfq_review_state import ReviewState, warning_disposition

PREVIEW_LABEL = "Governed v1.3 Workbook Review Preview"
PREVIEW_CAPTION = (
    "Controlled workbook intake, normalization, evidence and provenance review. "
    "Analytical handoff is available only for confirmed, fully governed Full Sourcing Review workbooks. "
    "This is not a v1.3 application release, autonomous award process, production deployment or live ERP integration."
)

FIELD_LABELS = {
    "OTIF_PERCENT": "OTIF (%)",
    "QUALITY_PPM": "Quality (ppm)",
    "SUPPLIER_AUDIT_SCORE": "Supplier audit score (0–100)",
    "COMPLAINT_RATE_PERCENT": "Complaint rate (%)",
    "CAPACITY_BUFFER_PERCENT": "Capacity buffer (%)",
    "RECYCLABILITY_PERCENT": "Recyclability (%)",
    "CERTIFICATION_SCORE": "Certification score (0–100)",
    "CARBON_SCORE": "Carbon score (0–100)",
    "EPR_READINESS_SCORE": "EPR readiness score (0–100)",
    "PCR_CONTENT_PERCENT": "PCR content (%)",
}


def _friendly_text(value: Any) -> str:
    """Convert internal identifiers to readable labels without exposing code formatting."""
    if value is None:
        return "—"
    text = str(value).strip()
    if not text:
        return "—"
    return text.replace("_", " ").title()


def _field_label(value: Any) -> str:
    text = str(value or "")
    return FIELD_LABELS.get(text, _friendly_text(text))


def _display_value(value: Any) -> Any:
    """Return scalar, business-readable values for Streamlit tables."""
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (date, datetime, Decimal, int, float)):
        return value
    if isinstance(value, Mapping):
        return "; ".join(f"{_friendly_text(key)}: {_display_value(item)}" for key, item in value.items()) or "—"
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return ", ".join(str(_display_value(item)) for item in value) or "—"
    return _friendly_text(value) if "_" in str(value) and str(value).upper() == str(value) else str(value)


def _unit_price(value: Any, currency: Any, uom: Any) -> str:
    if value is None or str(value).strip() == "":
        return "—"
    currency_text = str(currency or "").upper() or "Currency not stated"
    uom_text = str(uom or "").lower() or "unit not stated"
    try:
        amount = f"{float(value):,.4f}".rstrip("0").rstrip(".")
    except (TypeError, ValueError):
        amount = str(value)
    return f"{currency_text} {amount} / {uom_text}"


def _finding_rows(result: Any) -> list[dict[str, Any]]:
    return [{
        "Severity": _friendly_text(getattr(finding, "severity", "Information")),
        "Finding": _friendly_text(getattr(finding, "code", "Review finding")),
        "Message": getattr(finding, "message", str(finding)),
        "Sheet": _friendly_text(getattr(finding, "sheet", None)),
        "Row": getattr(finding, "row_number", None) or "—",
        "Field": _field_label(getattr(finding, "field_name", None)),
        "Source Row": getattr(finding, "source_row_id", None) or "—",
    } for finding in result.findings]


def render_findings(result: Any) -> None:
    rows = _finding_rows(result)
    if not rows:
        st.success("No governed findings were returned.")
        return
    frame = pd.DataFrame(rows)
    order = {"Fatal": 0, "Blocking": 1, "Warning": 2, "Information": 3}
    frame["_order"] = frame["Severity"].map(order).fillna(4)
    st.dataframe(frame.sort_values(["_order", "Finding"]).drop(columns="_order"), use_container_width=True, hide_index=True)


def render_mapping_reviews(adapter_result: Any) -> tuple[tuple[str, str, str], ...]:
    pending = [item for item in adapter_result.mapping_reviews if item.requires_confirmation and item.sheet != "SUPPLIER_RANKING_INPUTS"]
    if not pending:
        return ()
    st.subheader("Governed quotation mapping confirmation")
    confirmed: list[tuple[str, str, str]] = []
    for item in pending:
        label = f"{_friendly_text(item.sheet)}: '{item.source_header}' → {_field_label(item.canonical_field)}"
        checked = st.checkbox(label, value=False, key=f"mapping:{item.sheet}:{item.source_header}:{item.canonical_field}")
        st.caption(f"{_friendly_text(item.confidence_class)} | {item.reason or 'Explicit confirmation required'}")
        if checked and item.canonical_field:
            confirmed.append((item.sheet, item.source_header, item.canonical_field))
    return tuple(confirmed)


def render_ranking_mapping_confirmations(adapter_result: Any) -> tuple[RankingMappingConfirmation, ...]:
    """Create one typed confirmation for each alias and observed origin context."""
    pending = [item for item in adapter_result.mapping_reviews if item.requires_confirmation and item.sheet == "SUPPLIER_RANKING_INPUTS" and item.canonical_field]
    if not pending:
        return ()
    st.subheader("Governed ranking-field confirmation")
    confirmations: list[RankingMappingConfirmation] = []
    for item in pending:
        origins = sorted({
            str(record.value_origins.get(item.canonical_field) or "")
            for record in adapter_result.supplier_ranking_inputs
            if record.canonical_values.get(item.canonical_field) is not None
        })
        origins = [origin for origin in origins if origin]
        field_label = _field_label(item.canonical_field)
        st.write(f"**{item.source_header} → {field_label}**")
        origin_labels = ", ".join(_friendly_text(origin) for origin in origins) or "None detected"
        st.caption(f"Accepted scale: 0–100 | Required evidence origins: {origin_labels}")
        for origin in origins:
            key = f"ranking-mapping:{item.source_header}:{item.canonical_field}:{origin}"
            if st.checkbox(f"Confirm {field_label} for {_friendly_text(origin)}", value=False, key=key):
                confirmations.append(RankingMappingConfirmation(
                    upload_hash_sha256=adapter_result.upload_file_hash_sha256,
                    schema_version=adapter_result.schema_version,
                    alias_registry_version=adapter_result.alias_registry_version,
                    sheet="SUPPLIER_RANKING_INPUTS",
                    source_header=item.source_header,
                    canonical_field=str(item.canonical_field),
                    detected_scale="0_TO_100_ONLY",
                    value_origin=origin,
                ))
    return tuple(confirmations)


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
        label = _friendly_text(code)
        if disposition == "ACKNOWLEDGEMENT_REQUIRED":
            if st.checkbox(f"Acknowledge: {label}", value=False, key=f"warning:{code}"):
                acknowledged.append(code)
        elif disposition == "COMPATIBILITY_BLOCKING":
            st.error(f"{label}: analytical compatibility is blocked.")
        else:
            st.info(f"{label}: review information only.")
    return tuple(acknowledged)


def render_normalized_preview(orchestration_result: Any) -> None:
    rows: list[dict[str, Any]] = []
    for item in orchestration_result.enriched_quotes:
        values = item.record.canonical_values
        normalized = item.normalization.normalized_values
        source_currency = normalized.get("SOURCE_CURRENCY")
        source_uom = normalized.get("SOURCE_UOM")
        comparison_currency = normalized.get("COMPARISON_CURRENCY")
        comparison_uom = normalized.get("COMPARISON_UOM")
        rows.append({
            "RFQ Number": values.get("RFQ_NUMBER"),
            "RFQ Item": values.get("RFQ_ITEM"),
            "Supplier ID": values.get("SUPPLIER_ID"),
            "Supplier Name": values.get("SUPPLIER_NAME"),
            "Source Unit Price": _unit_price(normalized.get("SOURCE_PRICE"), source_currency, source_uom),
            "FX Rate": normalized.get("EXCHANGE_RATE_USED") if normalized.get("EXCHANGE_RATE_USED") is not None else "—",
            "FX Date": normalized.get("EXCHANGE_RATE_DATE_USED") or "—",
            "Normalized Unit Price": _unit_price(normalized.get("NORMALIZED_UNIT_PRICE"), comparison_currency, comparison_uom),
            "Source UOM": source_uom or "—",
            "Comparison UOM": comparison_uom or "—",
            "Eligible for Review": "Yes" if item.eligible_for_analysis else "No",
            "Evidence %": "—" if item.evidence is None else f"{float(item.evidence.coverage_percent):.1f}%",
            "History Match": "—" if item.historical_match is None else _friendly_text(item.historical_match.method),
            "Source Row": item.record.provenance.source_row_id,
        })
    if rows:
        st.caption("Unit prices include the applicable currency and unit of measure. FX rate converts the source currency to the comparison currency.")
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def render_compatibility(result: Any) -> None:
    compatibility = result.compatibility_result
    if compatibility is None:
        return
    st.subheader("Analytical compatibility")
    for blocker in compatibility.blockers:
        st.error(_friendly_text(blocker))
    rows = []
    for item in compatibility.manifest:
        values = getattr(item, "__dict__", {})
        rows.append({_friendly_text(key): _display_value(value) for key, value in values.items()})
    manifest = pd.DataFrame(rows)
    if not manifest.empty:
        st.dataframe(manifest, use_container_width=True, hide_index=True)


def render_handoff_confirmation(result: Any) -> bool:
    handoff = result.handoff_result
    if result.review_state is not ReviewState.READY_FOR_HANDOFF or handoff is None or not handoff.digest or handoff.manifest is None:
        return False
    st.subheader("Governed analytical handoff")
    st.write(f"**Selected RFQ:** {handoff.manifest.selected_rfq_number} | {handoff.manifest.selected_rfq_item}")
    st.write(f"**Suppliers:** {len(handoff.manifest.suppliers)}")
    st.write(f"**Analytical basis:** {handoff.manifest.analytical_currency} per {str(handoff.manifest.comparison_uom).lower()}")
    reference = f"{handoff.digest[:8]}…{handoff.digest[-4:]}"
    st.info(f"Confirmation reference: {reference}")
    st.caption("This reference binds the upload, selected item, supplier set, governed ranking evidence, commercial inputs and analytical assumptions. The full technical fingerprint is retained internally for audit.")
    confirmed = st.checkbox(
        "I confirm analytical handoff for this exact RFQ item, supplier set, governed ranking evidence and USD comparison basis.",
        value=False,
        key="governed_v13_handoff_ack",
    )
    return bool(confirmed and st.button("Confirm governed analytical handoff", type="primary"))


def render_governed_review(result: Any) -> None:
    st.header(PREVIEW_LABEL)
    st.caption(PREVIEW_CAPTION)
    st.write(f"**Review state:** {_friendly_text(result.review_state.value)}")
    if result.route_warning:
        st.warning(result.route_warning)
    if result.stop_reason:
        if result.review_state in {ReviewState.ADAPTER_FATAL, ReviewState.ORCHESTRATION_BLOCKED, ReviewState.ANALYSIS_INCOMPATIBLE}:
            st.error(result.stop_reason)
        else:
            st.warning(result.stop_reason)
    render_findings(result)
    if result.orchestration_result is not None:
        st.metric("Evidence coverage", f"{float(result.orchestration_result.event_coverage_percent):.1f}%")
        st.caption(f"Aggregation method: {_friendly_text(result.orchestration_result.event_aggregation_method)}")
        render_normalized_preview(result.orchestration_result)
    render_compatibility(result)
    if result.review_state is ReviewState.REVIEW_ONLY_COMPLETE:
        st.info("Governed review is complete. Analytical handoff remains disabled for this route or workbook.")
    elif result.review_state is ReviewState.HANDOFF_CONFIRMED:
        st.success("Governed analytical handoff confirmed for the displayed reference.")
