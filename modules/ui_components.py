"""Reusable executive-readable Streamlit presentation components."""

from __future__ import annotations

import re
from typing import Iterable

import pandas as pd
import plotly.express as px
import streamlit as st


def humanize_label(value: str) -> str:
    text = re.sub(r"[_-]+", " ", str(value or "")).strip()
    return " ".join(word.upper() if word.lower() in {"esg", "srm", "ai", "tco", "otif", "ppm", "epr", "pcr"} else word.capitalize() for word in text.split())


def format_display_value(value) -> str:
    """Render scalar and collection values without splitting strings character by character."""
    if value in (None, "", []):
        return "Not provided"
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple, set)):
        items = [str(item).strip() for item in value if str(item).strip()]
        return ", ".join(items) if items else "Not provided"
    return str(value)


def render_metric_card(label, value, help_text=None):
    st.metric(humanize_label(label), value, help=help_text)


def render_status_badge(label, status, message=None):
    text = f"**{humanize_label(label)}:** {status}"
    normalized = str(status).lower()
    if any(word in normalized for word in ["critical", "blocked", "insufficient", "high risk", "exit"]):
        st.error(text)
    elif any(word in normalized for word in ["limited", "warning", "review", "provisional", "development"]):
        st.warning(text)
    else:
        st.success(text)
    if message:
        st.caption(message)


def render_score_bar(label, score, caption=None):
    numeric = max(0.0, min(100.0, float(score or 0)))
    st.write(f"**{humanize_label(label)}:** {numeric:.1f}/100")
    st.progress(int(round(numeric)))
    if caption:
        st.caption(caption)


def render_score_matrix(scores: dict, columns=3):
    items = list(scores.items())
    for start in range(0, len(items), columns):
        row = st.columns(min(columns, len(items) - start))
        for container, (label, value) in zip(row, items[start:start + columns]):
            with container:
                render_metric_card(label, f"{float(value):.1f}/100")


def _render_lines(title: str, items: Iterable, empty_message: str):
    st.markdown(f"#### {title}")
    values = [str(item) for item in items or [] if str(item).strip()]
    if not values:
        st.info(empty_message)
        return
    for item in values:
        st.markdown(f"- {item}")


def render_evidence_list(items):
    _render_lines("Evidence", items, "No evidence was supplied.")


def render_strengths_panel(items):
    _render_lines("Strengths", items, "No verified leading strength has been confirmed.")


def render_gaps_panel(items):
    values = [str(item) for item in items or [] if str(item).strip()]
    st.markdown("#### Gaps and concerns")
    if not values:
        st.success("No material gap was identified from the available evidence.")
        return
    for item in values:
        st.warning(item)


def render_action_plan(items, owner="Procurement and supplier owner", cadence="Next formal review"):
    st.markdown("#### Recommended actions")
    values = [str(item) for item in items or [] if str(item).strip()]
    if not values:
        st.info("No additional action was generated.")
        return
    rows = []
    for index, item in enumerate(values, start=1):
        rows.append({
            "Priority": index,
            "Action": item,
            "Suggested owner": owner,
            "Review cadence": cadence,
        })
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def render_risk_alert(title, message, severity="warning"):
    text = f"**{title}**\n\n{message}"
    if severity == "error":
        st.error(text)
    elif severity == "success":
        st.success(text)
    else:
        st.warning(text)


def render_governance_note(message):
    st.info(message)


def render_data_completeness_card(score, status, evidence_quality=None):
    c1, c2, c3 = st.columns(3)
    c1.metric("Data completeness", f"{float(score or 0):.1f}%")
    c2.metric("Assessment status", status)
    c3.metric("Evidence quality", evidence_quality or "Not assessed")
    st.progress(int(round(max(0, min(100, float(score or 0))))))


def render_dimension_chart(title, dimensions: dict, y_title="Score"):
    frame = pd.DataFrame({"Dimension": [humanize_label(k) for k in dimensions], "Score": [max(0, min(100, float(v or 0))) for v in dimensions.values()]})
    fig = px.bar(frame, x="Dimension", y="Score", text_auto=".1f", range_y=[0, 100], title=title)
    fig.update_layout(xaxis_title=None, yaxis_title=y_title, margin=dict(l=10, r=10, t=50, b=10), legend_title_text="")
    st.plotly_chart(fig, width="stretch")


def render_comparison_matrix(frame: pd.DataFrame, title=None):
    if title:
        st.subheader(title)
    st.dataframe(frame, width="stretch", hide_index=True)


def render_executive_summary_card(title, text):
    st.markdown(f"### {title}")
    st.info(str(text))


def render_key_value_matrix(title: str, values: dict, columns=2):
    st.markdown(f"#### {title}")
    items = list(values.items())
    for start in range(0, len(items), columns):
        row = st.columns(min(columns, len(items) - start))
        for container, (label, value) in zip(row, items[start:start + columns]):
            with container:
                st.markdown(f"**{humanize_label(label)}**")
                st.write(format_display_value(value))


def build_readable_supplier_report(profile: dict) -> str:
    performance = profile.get("performance", {})
    financial = profile.get("financial", {})
    esg = profile.get("esg", {})
    innovation = profile.get("innovation", {})
    srm = profile.get("srm", {})
    lines = [
        "SUPPLIER 360 READABLE REPORT",
        "",
        f"Supplier: {profile.get('supplier_name', 'Not provided')}",
        f"Supplier 360 score: {profile.get('overall_supplier360_score', 0)}/100",
        f"Performance: {performance.get('overall_supplier_performance_score', 0)}/100 — {performance.get('performance_category', 'Not assessed')}",
        f"Financial assessment: {financial.get('assessment_status', 'Not assessed')} — displayed indicator {financial.get('displayed_financial_score', 0)}/100",
        f"ESG maturity: {esg.get('esg_maturity_level', 'Not assessed')} — {esg.get('displayed_esg_score', esg.get('esg_maturity_score', 0))}/100",
        f"Innovation maturity: {innovation.get('innovation_maturity_level', 'Not assessed')} — {innovation.get('displayed_innovation_score', innovation.get('innovation_score', 0))}/100",
        f"SRM classification: {srm.get('srm_classification', 'Not assessed')}",
        "",
        "Human approval remains mandatory. Financial, ESG and innovation indicators require evidence verification.",
    ]
    return "\n".join(lines)
