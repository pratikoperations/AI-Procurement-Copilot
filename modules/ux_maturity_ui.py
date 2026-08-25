"""Reusable presentation-only UX primitives for procurement decision hierarchy.

This module formats already-produced application evidence. It does not calculate,
score, qualify, recommend, allocate, approve or mutate procurement data.
"""
from __future__ import annotations

from contextlib import contextmanager
from collections.abc import Iterable, Iterator, Mapping, Sequence
from typing import Any

import streamlit as st

UX_MATURITY_CONTRACT = "AIPC-UX-MATURITY-1.0"

SEMANTIC_FAMILIES: dict[str, dict[str, str]] = {
    "supplier": {"accent": "#3B82F6", "label": "RFQ / SUPPLIER EVALUATION"},
    "cost": {"accent": "#0F766E", "label": "TCO / SHOULD COST"},
    "allocation": {"accent": "#0F8B8D", "label": "ALLOCATION / SCENARIOS"},
    "negotiation": {"accent": "#A16207", "label": "NEGOTIATION INTELLIGENCE"},
    "governance": {"accent": "#64748B", "label": "GOVERNANCE / ASSUMPTIONS"},
    "output": {"accent": "#2563EB", "label": "SYSTEM ANALYSIS / OUTPUT"},
}

_STATUS_TONES: dict[str, str] = {
    "eligible": "#2E8B57",
    "ready": "#2E8B57",
    "pass": "#2E8B57",
    "complete": "#2E8B57",
    "eligible with conditions": "#B7791F",
    "human review required": "#B7791F",
    "pass with warnings": "#B7791F",
    "warning": "#B7791F",
    "conditional": "#B7791F",
    "needs review": "#B7791F",
    "blocked": "#C53030",
    "ineligible": "#C53030",
    "infeasible": "#C53030",
    "insufficient data": "#64748B",
    "missing": "#64748B",
    "unknown": "#64748B",
    "not available": "#64748B",
    "not assessed": "#64748B",
}


def _family(name: str) -> dict[str, str]:
    return SEMANTIC_FAMILIES.get(name, SEMANTIC_FAMILIES["governance"])


def _escape(value: Any) -> str:
    text = str(value if value is not None else "Not available")
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render_page_context(
    title: str,
    purpose: str,
    context_items: Sequence[tuple[str, Any]] = (),
) -> None:
    """Render compact page orientation without a marketing-style hero."""
    st.markdown(f"## {_escape(title)}")
    st.caption(purpose)
    if context_items:
        compact = " · ".join(f"{_escape(label)}: **{_escape(value)}**" for label, value in context_items)
        st.markdown(compact, unsafe_allow_html=True)


def render_phase_label(
    family: str,
    phase: str,
    purpose: str | None = None,
) -> None:
    """Render a restrained semantic section marker with text-first meaning."""
    spec = _family(family)
    purpose_html = f"<div style='margin-top:0.15rem;color:var(--text-color);opacity:0.78;font-size:0.9rem'>{_escape(purpose)}</div>" if purpose else ""
    st.markdown(
        (
            f"<div style='border-left:4px solid {spec['accent']};padding:0.15rem 0 0.15rem 0.75rem;margin:0.1rem 0 0.7rem 0'>"
            f"<div style='font-size:0.72rem;font-weight:700;letter-spacing:0.055em;color:{spec['accent']}'>{_escape(spec['label'])}</div>"
            f"<div style='font-size:0.78rem;font-weight:650;letter-spacing:0.04em;color:var(--text-color);opacity:0.8'>{_escape(phase)}</div>"
            f"{purpose_html}</div>"
        ),
        unsafe_allow_html=True,
    )


@contextmanager
def semantic_section(
    family: str,
    phase: str,
    purpose: str | None = None,
) -> Iterator[None]:
    """Provide one responsive bordered surface for a major workflow section."""
    with st.container(border=True):
        render_phase_label(family, phase, purpose)
        yield


def _render_key_values(items: Sequence[tuple[str, Any]], columns: int = 4) -> None:
    values = list(items)
    if not values:
        return
    width = max(1, min(columns, len(values)))
    for start in range(0, len(values), width):
        row_items = values[start : start + width]
        row = st.columns(len(row_items))
        for container, (label, value) in zip(row, row_items):
            with container:
                st.caption(str(label))
                st.markdown(f"**{value if value not in (None, '') else 'Not available'}**")


def render_input_block(
    items: Sequence[tuple[str, Any]],
    *,
    title: str = "Current inputs and assumptions",
    columns: int = 4,
) -> None:
    """Distinguish user-selected context from system-produced analysis."""
    with st.container(border=True):
        render_phase_label("governance", "INPUT / ASSUMPTION", title)
        _render_key_values(items, columns=columns)


def render_status_chip(status: Any, *, label: str = "Status") -> None:
    """Render an accessible text-first status chip without changing status meaning."""
    text = str(status if status not in (None, "") else "Unknown")
    tone = _STATUS_TONES.get(text.casefold(), "#64748B")
    st.markdown(
        (
            f"<span role='status' aria-label='{_escape(label)}: {_escape(text)}' "
            f"style='display:inline-block;border:1px solid {tone};border-radius:999px;padding:0.22rem 0.55rem;"
            f"font-size:0.78rem;font-weight:700;color:{tone};background:color-mix(in srgb, {tone} 9%, transparent)'>"
            f"{_escape(label)} · {_escape(text)}</span>"
        ),
        unsafe_allow_html=True,
    )


def render_result_summary(
    items: Sequence[tuple[str, Any]],
    *,
    title: str = "Decision result",
    family: str = "output",
    status: Any | None = None,
    status_label: str = "Status",
    columns: int = 4,
) -> None:
    """Surface existing governed outputs without recalculating or duplicating full detail."""
    with st.container(border=True):
        render_phase_label(family, "SYSTEM ANALYSIS / OUTPUT", title)
        if status is not None:
            render_status_chip(status, label=status_label)
            st.write("")
        _render_key_values(items, columns=columns)


def render_governance_disclosure(
    lines: Iterable[Any],
    *,
    title: str = "Evidence & governance details",
) -> None:
    """Keep secondary audit context accessible without dominating the primary decision."""
    values = [str(item) for item in lines if str(item).strip()]
    with st.expander(title, expanded=False):
        if not values:
            st.caption("No additional governance detail is available for this view.")
            return
        for item in values:
            st.write(f"- {item}")
