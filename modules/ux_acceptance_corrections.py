"""Presentation-only hosted acceptance corrections.

This module does not alter authoritative calculations, scoring, qualification,
recommendation, allocation, RFQ processing, exports, or procurement authority.
It formats already-produced evidence for the active display context.
"""
from __future__ import annotations

from collections.abc import Mapping
from copy import copy
from dataclasses import is_dataclass, replace
from typing import Any

import pandas as pd

from modules.utils import build_currency_display_frame, normalize_display_currency


def _display_context() -> tuple[str, float]:
    """Return the published display currency and FX rate, failing closed to USD."""
    try:
        from modules.sourcemate_global_context import current_context

        context = current_context()
        currency = normalize_display_currency(context.get("display_currency") or "USD")
        fx_rate = float(context.get("fx_rate") or 0)
        if currency in {"INR", "Both"} and fx_rate <= 0:
            return "USD", 1.0
        return currency, fx_rate or 1.0
    except Exception:
        return "USD", 1.0


def _business_label(column: str) -> str:
    label = str(column).replace("_", " ").strip()
    for suffix in (" (USD)", " USD", " usd"):
        if label.endswith(suffix):
            label = label[: -len(suffix)]
            break
    return " ".join(word.capitalize() if word.islower() else word for word in label.split())


def _currency_mapping(frame: pd.DataFrame) -> dict[str, str]:
    """Map canonical USD columns to readable display labels."""
    mapping: dict[str, str] = {}
    for column in frame.columns:
        name = str(column)
        lowered = name.lower()
        if lowered.endswith("_usd") or lowered.endswith(" usd") or lowered.endswith("(usd)"):
            mapping[name] = _business_label(name)
    return mapping


def build_contextual_currency_frame(
    frame: pd.DataFrame,
    display_currency: str | None = None,
    fx_rate: float | None = None,
) -> pd.DataFrame:
    """Return a presentation-only currency frame without mutating canonical data."""
    if not isinstance(frame, pd.DataFrame) or frame.empty:
        return frame.copy() if isinstance(frame, pd.DataFrame) else frame
    if display_currency is None or fx_rate is None:
        context_currency, context_fx = _display_context()
        display_currency = display_currency or context_currency
        fx_rate = context_fx if fx_rate is None else fx_rate
    mapping = _currency_mapping(frame)
    if not mapping:
        return frame.copy()
    return build_currency_display_frame(
        frame.copy(),
        mapping,
        normalize_display_currency(display_currency),
        float(fx_rate),
    )


def flatten_evidence_rows(value: Any, prefix: str = "") -> list[dict[str, str]]:
    """Flatten nested audit evidence into business-readable field/value rows."""
    rows: list[dict[str, str]] = []
    if isinstance(value, Mapping):
        if not value:
            return [{"Evidence field": prefix or "Evidence", "Value": "Not available"}]
        for key, nested in value.items():
            path = f"{prefix} › {_business_label(str(key))}" if prefix else _business_label(str(key))
            rows.extend(flatten_evidence_rows(nested, path))
        return rows
    if isinstance(value, (list, tuple)):
        if not value:
            return [{"Evidence field": prefix or "Evidence", "Value": "None recorded"}]
        for index, nested in enumerate(value, start=1):
            path = f"{prefix} › Item {index}" if prefix else f"Item {index}"
            rows.extend(flatten_evidence_rows(nested, path))
        return rows
    if isinstance(value, bool):
        text = "Yes" if value else "No"
    elif value is None or value == "":
        text = "Not available"
    elif isinstance(value, float):
        text = f"{value:,.4f}".rstrip("0").rstrip(".")
    else:
        text = str(value)
    return [{"Evidence field": prefix or "Evidence", "Value": text}]


def _render_evidence_table(st: Any, value: Any, caption: str | None = None) -> None:
    rows = flatten_evidence_rows(value)
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    if caption:
        st.caption(caption)


def _copy_with_display_allocation(value: Any, currency: str, fx_rate: float) -> Any:
    """Copy a scenario presentation and replace only its displayed allocation frame."""
    allocation = getattr(value, "allocation_df", None)
    if not isinstance(allocation, pd.DataFrame):
        return value
    display = build_contextual_currency_frame(allocation, currency, fx_rate)
    try:
        if is_dataclass(value):
            return replace(value, allocation_df=display)
        cloned = copy(value)
        setattr(cloned, "allocation_df", display)
        return cloned
    except Exception:
        return value


def install_ux_acceptance_corrections() -> None:
    """Install bounded presentation wrappers once per interpreter."""
    try:
        import streamlit as st
        from modules import procurement_intelligence_ui as procurement_ui

        if not getattr(procurement_ui.render_procurement_intelligence, "_aipc_currency_context", False):
            original_render = procurement_ui.render_procurement_intelligence
            original_scenario_presenter = procurement_ui.build_scenario_presentation

            def scenario_presenter_with_currency(*args: Any, **kwargs: Any):
                result = original_scenario_presenter(*args, **kwargs)
                currency, fx_rate = _display_context()
                return _copy_with_display_allocation(result, currency, fx_rate)

            def render_procurement_intelligence_with_currency(
                decision,
                strategy,
                optimized_allocation,
                negotiation_df,
                risk_result,
                scenario_result,
                executive_narrative,
                *,
                recommendation_allowed=True,
            ):
                currency, fx_rate = _display_context()
                allocation_bundle = dict(optimized_allocation)
                allocation = allocation_bundle.get("allocation_df")
                if isinstance(allocation, pd.DataFrame):
                    allocation_bundle["allocation_df"] = build_contextual_currency_frame(
                        allocation, currency, fx_rate
                    )
                negotiation_display = build_contextual_currency_frame(
                    negotiation_df, currency, fx_rate
                )
                procurement_ui.build_scenario_presentation = scenario_presenter_with_currency
                try:
                    return original_render(
                        decision,
                        strategy,
                        allocation_bundle,
                        negotiation_display,
                        risk_result,
                        scenario_result,
                        executive_narrative,
                        recommendation_allowed=recommendation_allowed,
                    )
                finally:
                    procurement_ui.build_scenario_presentation = original_scenario_presenter

            render_procurement_intelligence_with_currency._aipc_currency_context = True
            procurement_ui.render_procurement_intelligence = render_procurement_intelligence_with_currency
    except Exception:
        pass

    try:
        from modules import calculation_explorer_ui as explorer

        if not getattr(explorer._render_result, "_aipc_business_evidence", False):
            def render_result_business_first(item):
                prepared = explorer._prepare_result_presentation(item)
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
                with st.expander("Canonical audit evidence", expanded=False):
                    _render_evidence_table(
                        st,
                        prepared["technical_payload"],
                        "Authoritative payload retained for audit. Values are not recalculated by the Explorer.",
                    )

            def render_trace_business_first(presentation):
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
                sections = (
                    ("Input summary", trace.get("input_snapshot") or {}),
                    ("Authoritative output summary", trace.get("raw_output")),
                    ("Intermediate steps and unavailable parameters", {
                        "intermediate_steps": trace.get("intermediate_steps") or (),
                        "unresolved_or_rejected_parameters": trace.get("unresolved_or_rejected_parameters") or (),
                    }),
                    ("Governed decision impact", {
                        "blocking_rule_record": trace.get("blocking_rule_record"),
                        "recommendation_impact": trace.get("recommendation_impact"),
                    }),
                )
                for title, value in sections:
                    with st.expander(title, expanded=False):
                        _render_evidence_table(st, value)
                if trace.get("configuration_versions_status") == "satisfied":
                    with st.expander("Configuration versions", expanded=False):
                        _render_evidence_table(st, trace.get("configuration_versions"))
                else:
                    st.warning(trace.get("configuration_versions_note") or "Configuration-version evidence is unavailable.")

            def render_reconciliation_business_first(presentation):
                item = presentation["reconciliation_summary"]
                explorer._status_message(str(item.get("classification")), str(item.get("blocking_status")))
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
                    _render_evidence_table(st, {
                        "exact_matches": item.get("exact_matches") or (),
                        "tolerated_differences": item.get("tolerated_differences") or (),
                        "mismatches": item.get("mismatches") or (),
                        "unavailable_evidence": item.get("unavailable_evidence") or (),
                        "tolerance_rules": item.get("tolerance_rules") or (),
                    })

            render_result_business_first._aipc_business_evidence = True
            explorer._render_result = render_result_business_first
            explorer._render_trace = render_trace_business_first
            explorer._render_reconciliation = render_reconciliation_business_first
    except Exception:
        pass
