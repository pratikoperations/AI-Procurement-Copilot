"""Presentation-only decision clarity helpers for the portfolio application.

This module does not calculate, score, rank, qualify, recommend, allocate or
approve. It formats already-produced application evidence so a first-time user
can understand the active decision context before opening detailed analysis.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import streamlit as st

from modules.unit_display import format_annual_volume
from modules.utils import unit_cost
from modules.ux_maturity_ui import (
    render_governance_disclosure,
    render_input_block,
    render_result_summary,
    semantic_section,
)

DECISION_CLARITY_CONTRACT = "AIPC-UX-DECISION-CLARITY-1.0"


def _value(row: Mapping[str, Any], *keys: str, fallback: Any = None) -> Any:
    for key in keys:
        value = row.get(key)
        if value is not None and value != "":
            return value
    return fallback


def _eligibility_label(row: Mapping[str, Any]) -> str:
    value = _value(row, "technical_eligible", "eligibility", fallback=None)
    if isinstance(value, bool):
        return "Eligible" if value else "Ineligible"
    text = str(value or "Not available").strip()
    return text if text else "Not available"


def build_context_strip(assumptions: Mapping[str, Any]) -> tuple[tuple[str, str], ...]:
    """Return a stable context strip from existing user selections."""
    currency = str(assumptions.get("display_currency") or "USD")
    fx_rate = assumptions.get("fx_rate")
    fx_text = "Not required" if currency == "USD" else (
        f"{float(fx_rate):.2f} INR/USD" if fx_rate is not None else "Unavailable"
    )
    scenario = str(
        assumptions.get("procurement_intelligence_scenario")
        or assumptions.get("scenario")
        or "Base"
    )
    return (
        ("Category", str(assumptions.get("category") or "Not selected")),
        ("Commodity", str(assumptions.get("commodity") or "Not selected")),
        ("Scenario", scenario),
        ("Currency", currency),
        ("FX rate", fx_text),
        ("Data source", str(assumptions.get("data_source") or "Controlled demonstration")),
        ("Decision status", "Human review required"),
    )


def build_decision_card(
    scored_rows: Sequence[Mapping[str, Any]],
    assumptions: Mapping[str, Any],
    confidence: Any = None,
) -> dict[str, str]:
    """Build a read-only decision card from the already-ranked result rows."""
    if not scored_rows:
        return {
            "supplier": "No result available",
            "eligibility": "Not available",
            "quote": "Not available",
            "tco": "Not available",
            "risk": "Not available",
            "confidence": "Pending",
            "action": "Review input evidence before making a sourcing decision.",
            "approval": "Human procurement approval required",
        }

    recommended = scored_rows[0]
    display_currency = str(assumptions.get("display_currency") or "USD")
    fx_rate = float(assumptions.get("fx_rate") or 83.0)
    quote = _value(recommended, "Quoted Unit Price USD", "quote_usd", fallback=None)
    tco = _value(recommended, "adjusted_tco_unit_usd", "tco_adjusted_rate_usd", fallback=None)
    risk = _value(recommended, "risk_category", "risk", fallback=None)
    risk_score = _value(recommended, "risk_score", fallback=None)
    risk_text = str(risk or "Not available")
    if risk_score is not None:
        risk_text = f"{risk_text} ({risk_score}/100)"

    supplier = str(_value(recommended, "Supplier", "supplier", fallback="Not available"))
    eligibility = _eligibility_label(recommended)
    if eligibility.lower().startswith("ineligible"):
        action = "Do not progress to award; review qualification failures and remediation evidence."
    else:
        action = "Review the commercial gap, risk evidence and negotiation priorities before approval."

    return {
        "supplier": supplier,
        "eligibility": eligibility,
        "quote": unit_cost(float(quote), display_currency, fx_rate) if quote is not None else "Not available",
        "tco": unit_cost(float(tco), display_currency, fx_rate) if tco is not None else "Not available",
        "risk": risk_text,
        "confidence": f"{confidence}/100" if confidence is not None else "Pending",
        "action": action,
        "approval": "Human procurement approval required",
    }


def interview_demo_steps() -> tuple[str, ...]:
    """Return the approved five-minute demonstration path."""
    return (
        "Confirm the active category, commodity, scenario, currency and data source.",
        "Read the executive decision card and identify the current leading supplier.",
        "Open Decision Summary to compare RFQ quote, TCO, eligibility, risk and value.",
        "Open Cost and Risk to show should-cost evidence and the governed TCO breakdown.",
        "Open Scenarios and Negotiation to demonstrate stress testing and negotiation preparation.",
        "Ask SourceMate one controlled question, then show trace, governance evidence or exports.",
        "Close by confirming that human procurement approval remains mandatory.",
    )


def render_decision_clarity(scored_df, assumptions: Mapping[str, Any], confidence: Any = None) -> None:
    """Render context, existing decision outputs and optional demonstration guidance."""
    records = scored_df.to_dict("records") if hasattr(scored_df, "to_dict") else list(scored_df or [])
    context = build_context_strip(assumptions)
    card = build_decision_card(records, assumptions, confidence)

    st.subheader("Decision at a glance")
    render_input_block(
        (
            *context[:6],
            (
                "Annual volume",
                format_annual_volume(
                    assumptions.get("annual_volume", 0),
                    assumptions.get("annual_volume_unit", "unit"),
                ),
            ),
        ),
        title="Current sourcing context",
        columns=4,
    )

    render_result_summary(
        (
            ("Leading supplier", card["supplier"]),
            ("RFQ quote", card["quote"]),
            ("TCO unit cost", card["tco"]),
            ("Risk", card["risk"]),
            ("Decision confidence", card["confidence"]),
        ),
        title="Current governed decision result",
        family="supplier",
        status=card["eligibility"],
        status_label="Qualification",
        columns=3,
    )

    with semantic_section(
        "supplier",
        "RECOMMENDATION / DECISION OUTPUT",
        "Translate the current governed result into the next human procurement review step.",
    ):
        st.markdown(f"**Recommended next action:** {card['action']}")
        st.caption(card["approval"] + ". This view explains existing results and does not create an award decision.")

    render_governance_disclosure(
        (
            dict(context).get("Decision status", "Human review required"),
            "Detailed technical and governance evidence remains available in the relevant workflow sections.",
            "No approval, supplier award or ERP writeback is created by this presentation layer.",
        ),
        title="Decision governance",
    )

    with st.expander("Five-minute interview demonstration path", expanded=False):
        for index, step in enumerate(interview_demo_steps(), start=1):
            st.write(f"**{index}.** {step}")

    with st.expander("How detailed evidence is organized", expanded=False):
        st.write("- **Decision Summary:** supplier comparison and business value.")
        st.write("- **Cost and Risk:** should-cost, TCO and category-risk assumptions.")
        st.write("- **Scenarios and Negotiation:** allocation, stress tests and negotiation preparation.")
        st.write("- **Procurement and Supplier Intelligence:** deeper risk, SRM, ESG and performance evidence.")
        st.write("- **Executive Outputs and Downloads:** reviewable communication and export evidence.")
        st.caption("Detailed technical and governance evidence remains available but is not shown before the core decision.")
