"""Currency-aware presentation wrapper for the Governed Calculation Explorer."""
from __future__ import annotations

from collections.abc import Mapping as MappingABC
from typing import Any, Mapping

import pandas as pd
import streamlit as st

from modules.calculation_explorer_evidence_ui import (
    render_readable_reconciliation,
    render_readable_trace,
)
from modules.calculation_explorer_ui import (
    SECTIONS,
    _find_principal_result_key,
    _format_result_value,
    _humanize_result_field,
    _render_assumptions,
    _render_human_review,
    _render_sourcemate,
    _result_unit,
)
from modules.config import DEFAULT_FX_RATE
from modules.utils import normalize_display_currency

_NON_MONETARY_KEYS = {
    "commodity",
    "category",
    "supplier",
    "scenario",
    "commodity_index",
    "score",
    "risk_score",
    "performance_score",
}
_METADATA_KEYS = {"unit", "currency", "uom", "principal_result_key"}


def _replace_currency_unit(unit: str, mode: str) -> str:
    canonical = str(unit or "").strip()
    if not canonical:
        return mode
    if mode == "USD":
        return canonical
    inr = canonical.replace("USD", "INR")
    if mode == "INR":
        return inr
    return f"{canonical} / {inr}"


def _display_value(value: Any, key: str, mode: str, fx_rate: float) -> str:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or key in _NON_MONETARY_KEYS:
        return _format_result_value(value)
    amount = float(value)
    if mode == "USD":
        return _format_result_value(amount)
    if mode == "INR":
        return f"{amount * fx_rate:,.2f}"
    return f"USD {_format_result_value(amount)} / INR {amount * fx_rate:,.2f}"


def _component_unit(key: str, canonical_unit: str, mode: str) -> str:
    if key in {"commodity", "category", "supplier", "scenario"}:
        return ""
    if key.endswith("_index") or key == "commodity_index":
        return "Index"
    return _replace_currency_unit(canonical_unit, mode)


def _component_rows(
    result: Mapping[str, Any],
    principal_key: str | None,
    canonical_unit: str,
    mode: str,
    fx_rate: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key, value in result.items():
        if key in _METADATA_KEYS or key == principal_key:
            continue
        if isinstance(value, MappingABC):
            for nested_key, nested_value in value.items():
                name = str(nested_key)
                rows.append({
                    "Component": _humanize_result_field(name),
                    "Value": _display_value(nested_value, name, mode, fx_rate),
                    "Unit": _component_unit(name, canonical_unit, mode),
                })
            continue
        name = str(key)
        rows.append({
            "Component": _humanize_result_field(name),
            "Value": _display_value(value, name, mode, fx_rate),
            "Unit": _component_unit(name, canonical_unit, mode),
        })
    return rows


def _canonical_payload_label(key: str) -> str:
    """Humanize a canonical key without dropping explicit currency suffixes."""
    label = _humanize_result_field(key)
    upper_key = key.upper()
    if upper_key.endswith("_USD") and not label.endswith(" USD"):
        return f"{label} USD"
    if upper_key.endswith("_INR") and not label.endswith(" INR"):
        return f"{label} INR"
    return label


def _canonical_payload_value(value: Any) -> str:
    """Format canonical values consistently without changing their meaning."""
    if isinstance(value, float):
        return f"{value:,.2f}"
    return _format_result_value(value)


def prepare_canonical_payload_rows(payload: Any) -> list[dict[str, str]]:
    """Flatten the unchanged canonical payload into an interview-readable table."""
    rows: list[dict[str, str]] = []

    def append_value(field_path: tuple[str, ...], value: Any) -> None:
        if isinstance(value, MappingABC):
            for key, nested_value in value.items():
                append_value((*field_path, str(key)), nested_value)
            return
        label = " › ".join(_canonical_payload_label(part) for part in field_path)
        rows.append({"Field": label or "Result", "Value": _canonical_payload_value(value)})

    if isinstance(payload, MappingABC):
        for key, value in payload.items():
            append_value((str(key),), value)
    else:
        append_value((), payload)
    return rows


def prepare_currency_result_presentation(
    item: Mapping[str, Any],
    display_currency: str = "USD",
    fx_rate: float = DEFAULT_FX_RATE,
) -> dict[str, Any]:
    """Build a display-only currency view while retaining the canonical payload."""
    mode = normalize_display_currency(display_currency)
    rate = float(fx_rate)
    if rate <= 0:
        raise ValueError("FX rate must be positive.")

    result = item.get("result")
    canonical_unit = _result_unit(item, result)
    if result is None or result == "" or result == {}:
        return {
            "status": "unavailable",
            "display_currency": mode,
            "fx_rate": rate,
            "technical_payload": result,
        }

    if not isinstance(result, MappingABC):
        return {
            "status": "scalar",
            "display_currency": mode,
            "fx_rate": rate,
            "principal": {
                "label": "Result",
                "value": _display_value(result, "result", mode, rate),
                "unit": _replace_currency_unit(canonical_unit, mode),
            },
            "components": [],
            "technical_payload": result,
        }

    principal_key = _find_principal_result_key(item, result)
    principal = None
    if principal_key is not None:
        principal = {
            "key": principal_key,
            "label": _humanize_result_field(principal_key),
            "value": _display_value(result.get(principal_key), principal_key, mode, rate),
            "unit": _replace_currency_unit(canonical_unit, mode),
        }
    return {
        "status": "mapping",
        "display_currency": mode,
        "fx_rate": rate,
        "principal": principal,
        "components": _component_rows(result, principal_key, canonical_unit, mode, rate),
        "technical_payload": result,
    }


def _render_currency_result(item: Mapping[str, Any], display_currency: str, fx_rate: float) -> None:
    prepared = prepare_currency_result_presentation(item, display_currency, fx_rate)
    if prepared["status"] == "unavailable":
        st.info("Calculation result not available. No value has been fabricated.")
        return

    mode = prepared["display_currency"]
    st.caption(
        f"Business-facing values are displayed in {mode}. Canonical calculation, trace and reconciliation remain in USD. "
        f"FX rate: {prepared['fx_rate']:,.2f} INR/USD."
    )
    principal = prepared.get("principal")
    if principal:
        value = principal["value"]
        if principal.get("unit"):
            value = f"{value} {principal['unit']}"
        st.metric(principal["label"], value)

    components = prepared.get("components") or []
    if components:
        st.write("**Calculation components**")
        st.dataframe(pd.DataFrame(components), use_container_width=True, hide_index=True)

    with st.expander("Canonical result details — USD", expanded=False):
        canonical_rows = prepare_canonical_payload_rows(prepared["technical_payload"])
        st.dataframe(pd.DataFrame(canonical_rows), use_container_width=True, hide_index=True)
        st.caption("Canonical authoritative values are retained unchanged. Display conversion is not used for trace or reconciliation.")


def _render_currency_overview(
    presentation: Mapping[str, Any], display_currency: str, fx_rate: float
) -> None:
    item = presentation["calculation_overview"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Calculation", item.get("calculation_id") or "Not available")
    c2.metric("Formula", f"{item.get('formula_id')} v{item.get('formula_version')}")
    c3.metric("Category", item.get("category") or "Not available")
    c4.metric("Status", item.get("status") or "Not available")
    st.write(f"**Business name:** {item.get('business_name')}")
    st.write(f"**Authoritative source:** `{item.get('source_module')}::{item.get('source_function')}`")
    _render_currency_result(item, display_currency, fx_rate)
    st.write(f"**Owner:** {item.get('owner')}")
    st.write("**Downstream outputs:** " + ", ".join(item.get("downstream_outputs") or ("None registered",)))
    with st.expander("Formula documentation — non-executable", expanded=False):
        st.code(str(item.get("formula_text") or "No documented expression"), language=None)
        st.caption("Formula metadata is documentation only. The Explorer never evaluates it.")


def render_currency_aware_calculation_explorer(
    presentation: Mapping[str, Any],
    display_currency: str = "USD",
    fx_rate: float = DEFAULT_FX_RATE,
) -> None:
    """Render six sections with currency-aware and business-readable presentation."""
    st.header("Governed Calculation Explorer")
    st.caption("Read-only explanation of authoritative procurement calculations, assumptions, evidence and review status.")
    status = st.columns(4)
    status[0].info("Authoritative services")
    status[1].info("Formula metadata non-executable")
    status[2].info("Evidence disclosed")
    status[3].info("Human approval mandatory")
    section = st.radio("Explorer section", SECTIONS, horizontal=True, label_visibility="collapsed")
    if section == "Overview":
        _render_currency_overview(presentation, display_currency, fx_rate)
        return
    renderers = {
        "Assumptions": _render_assumptions,
        "Calculation Trace": render_readable_trace,
        "Reconciliation": render_readable_reconciliation,
        "SourceMate": _render_sourcemate,
        "Human Review": _render_human_review,
    }
    renderers[section](presentation)
