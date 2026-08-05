"""Read-only global SourceMate decision context.

This module publishes already-produced application outputs for explanation. It does
not calculate, score, rank, recommend, allocate, approve, or mutate procurement data.
"""
from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

logger = logging.getLogger(__name__)

GLOBAL_CONTEXT_CONTRACT = "AIPC-SOURCEMATE-GLOBAL-CONTEXT-1.0"
_CONTEXT_KEY = "sourcemate_global_decision_context"
_ACTIVE_PAGE_KEY = "sourcemate_active_page"

_COLUMN_ALIASES = {
    "supplier": ("Supplier", "Supplier Name", "Vendor", "Vendor Name"),
    "quote": ("Quoted Unit Price USD", "Quoted Unit Price", "Quoted Rate", "Quote"),
    "quote_currency": ("Quotation Currency", "Currency", "Quote Currency"),
    "normalized_rate": (
        "Normalized Unit Price USD",
        "Normalized Quote USD",
        "Comparison Unit Price USD",
        "Quoted Unit Price USD",
    ),
    "tco_adjusted_rate": (
        "TCO Adjusted Unit Cost USD",
        "TCO Adjusted Cost USD",
        "TCO Adjusted Price USD",
        "Total Cost USD",
        "TCO USD",
    ),
    "score": ("Overall Score", "Composite Score", "Final Score", "Supplier Score"),
    "rank": ("Rank", "Supplier Rank", "Overall Rank"),
    "risk": ("Risk Score", "Overall Risk Score", "Risk Category"),
    "eligibility": (
        "Eligibility Status",
        "Technical Eligibility",
        "Eligibility",
        "Eligible",
        "Technical Qualification",
        "Application Approval Status",
    ),
    "unit": ("Unit", "Comparison Unit", "UOM"),
}

GLOSSARY = {
    "RFQ": "Request for Quotation — a controlled request used to collect and compare supplier commercial offers.",
    "TCO": "Total Cost of Ownership — quoted price plus applicable freight, inventory, working-capital, risk and lead-time effects.",
    "SRM": "Supplier Relationship Management — structured classification and governance of supplier relationships.",
    "ESG": "Environmental, Social and Governance.",
    "OTIF": "On Time In Full — the percentage of orders delivered on time and in the full required quantity.",
    "EPR": "Extended Producer Responsibility — producer responsibility for post-use collection, recycling or compliant disposal.",
    "PCR": "Post-Consumer Recycled content — material recovered after consumer use and incorporated into a new product.",
    "FX": "Foreign Exchange — the conversion relationship between currencies, such as USD and INR.",
    "MOQ": "Minimum Order Quantity — the smallest quantity a supplier will accept for an order.",
    "DDP": "Delivered Duty Paid — seller bears delivery, duty and import-clearance obligations to the named destination.",
    "DAP": "Delivered At Place — seller delivers to the named place; buyer normally handles import clearance and duties.",
    "CIF": "Cost, Insurance and Freight — seller covers cost, insurance and freight to the named port; risk transfers under the applicable Incoterm rule.",
    "FOB": "Free On Board — seller delivers goods on board the vessel at the named port; buyer assumes subsequent freight and risk.",
    "EXW": "Ex Works — buyer takes responsibility from the seller's premises, subject to the agreed Incoterm wording.",
    "PPM": "Parts Per Million — a quality-defect measure representing defective parts per million supplied.",
    "GSM": "Grams per Square Metre — basis weight used for paper, board and related substrates.",
    "BF": "Burst Factor — a paper-strength indicator used with GSM and burst strength.",
    "UOM": "Unit of Measure.",
    "SLA": "Service Level Agreement.",
    "KPI": "Key Performance Indicator.",
    "should-cost": "A governed target-cost estimate based on registered cost drivers and assumptions; it is not a supplier invoice or autonomous award price.",
    "canonical currency": "The authoritative currency used by the calculation or comparison service before optional display conversion.",
    "reconciliation": "A comparison between authoritative evidence and presented or exported evidence, with exact, tolerated, mismatch and unavailable classifications.",
    "eligibility": "A hard qualification gate determining whether a supplier may proceed to comparison or recommendation.",
    "qualification": "Evidence-based confirmation that required technical, commercial or governance conditions are met.",
    "recommendation": "A decision-support output produced by existing governed logic; it does not approve or award a supplier.",
    "allocation": "A governed proposed distribution of volume across suppliers, subject to capacity, concentration and continuity constraints.",
    "confidence": "A bounded indication of evidence completeness and decision reliability, not certainty or approval authority.",
    "provenance": "The recorded origin of a value, assumption, formula, source module or evidence item.",
    "trace": "A deterministic record of the governed calculation path, inputs, intermediate evidence and configuration versions.",
    "human review": "Mandatory procurement review and approval retained outside SourceMate and outside autonomous execution.",
}


def _st():
    import streamlit as st
    return st


def _first(row: Mapping[str, Any], aliases: tuple[str, ...]) -> Any:
    for name in aliases:
        value = row.get(name)
        if value is not None and value != "":
            return value
    return None


def set_active_page(page: str) -> None:
    st = _st()
    st.session_state[_ACTIVE_PAGE_KEY] = str(page or "Unknown page")
    if "ERP Upload Preview" in str(page or ""):
        st.session_state[_CONTEXT_KEY] = {
            "contract_version": GLOBAL_CONTEXT_CONTRACT,
            "active_page": str(page),
            "context_type": "structural_preview",
            "supplier_rows": [],
            "data_source": "Uploaded workbook structural preview",
            "human_review_required": True,
            "evidence_references": ["pages/9_ERP_Upload_Preview.py"],
        }


def publish_scored_context(scored_df: Any, assumptions: Mapping[str, Any] | None = None) -> None:
    """Publish existing scored output without altering or recalculating it."""
    st = _st()
    assumptions = dict(assumptions or {})
    try:
        records = scored_df.to_dict(orient="records")
    except (AttributeError, TypeError) as exc:
        logger.warning(
            "SourceMate scored context received non-tabular output; publishing an empty supplier set.",
            extra={
                "event": "sourcemate_context_publish_fallback",
                "error_type": type(exc).__name__,
            },
        )
        records = []
    supplier_rows: list[dict[str, Any]] = []
    for position, row in enumerate(records, start=1):
        if not isinstance(row, Mapping):
            continue
        published = {key: _first(row, aliases) for key, aliases in _COLUMN_ALIASES.items()}
        published["rank"] = published.get("rank") or position
        published["recommendation_status"] = "Recommended" if position == 1 else "Alternative"
        published["available_fields"] = sorted(str(key) for key, value in row.items() if value is not None and value != "")
        supplier_rows.append(published)
    data_source = assumptions.get("data_source") or "Unknown"
    st.session_state[_CONTEXT_KEY] = {
        "contract_version": GLOBAL_CONTEXT_CONTRACT,
        "active_page": st.session_state.get(_ACTIVE_PAGE_KEY, "Main application"),
        "context_type": "scored_supplier_results",
        "data_source": data_source,
        "synthetic_demo": data_source == "Synthetic Demo",
        "category": assumptions.get("category"),
        "commodity": assumptions.get("commodity"),
        "display_currency": assumptions.get("display_currency"),
        "fx_rate": assumptions.get("fx_rate"),
        "scenario": assumptions.get("procurement_intelligence_scenario"),
        "annual_volume": assumptions.get("annual_volume"),
        "annual_volume_unit": assumptions.get("annual_volume_unit"),
        "supplier_rows": supplier_rows,
        "human_review_required": True,
        "action_executed": False,
        "evidence_references": [
            "modules/scoring.py::enrich_supplier_scores",
            "modules/data_loader.py",
            "app.py",
        ],
    }


def publish_selected_presentation(presentation: Mapping[str, Any]) -> None:
    """Merge selected-calculation evidence into the global context."""
    st = _st()
    current = dict(st.session_state.get(_CONTEXT_KEY) or {})
    current.update(
        {
            "contract_version": GLOBAL_CONTEXT_CONTRACT,
            "active_page": st.session_state.get(_ACTIVE_PAGE_KEY, "Governed Calculation Explorer"),
            "selected_presentation": dict(presentation or {}),
            "human_review_required": True,
            "action_executed": False,
        }
    )
    st.session_state[_CONTEXT_KEY] = current


def current_context(page: str | None = None) -> dict[str, Any]:
    st = _st()
    if page:
        set_active_page(page)
    context = dict(st.session_state.get(_CONTEXT_KEY) or {})
    context.setdefault("contract_version", GLOBAL_CONTEXT_CONTRACT)
    context.setdefault("active_page", st.session_state.get(_ACTIVE_PAGE_KEY, page or "Unknown page"))
    context.setdefault("supplier_rows", [])
    context.setdefault("human_review_required", True)
    context.setdefault("action_executed", False)
    context.setdefault("glossary", GLOSSARY)
    context.setdefault("calculation_overview", {})
    context.setdefault("assumptions", [])
    context.setdefault("calculation_trace", {"available": False})
    context.setdefault("reconciliation", {"available": False})
    context.setdefault("sourcemate", {"limitations": ["No web browsing.", "Human approval remains mandatory."]})
    selected = context.get("selected_presentation")
    if isinstance(selected, Mapping):
        for key in ("calculation_overview", "assumptions", "calculation_trace", "reconciliation", "sourcemate"):
            if selected.get(key) is not None:
                context[key] = selected.get(key)
    return context
