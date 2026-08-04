"""Focused assurance for readable Trace and Reconciliation presentation."""
from __future__ import annotations

from pathlib import Path

from modules.calculation_explorer_evidence_ui import (
    prepare_reconciliation_presentation,
    prepare_trace_presentation,
)


def test_trace_summary_humanizes_raw_output_without_mutating_payload():
    raw_output = {
        "commodity_index": 1.05,
        "target_unit_cost_usd": 1.27,
        "commodity": "PET Resin",
    }
    trace = {
        "input_snapshot": {"route": "PET Resin should-cost", "mode": "controlled demonstration"},
        "raw_output": raw_output,
        "intermediate_steps": (),
        "unresolved_or_rejected_parameters": (),
        "blocking_rule_record": None,
        "recommendation_impact": "No direct impact",
        "configuration_versions_status": "satisfied",
        "configuration_versions": {"catalogue": "1.0"},
    }

    prepared = prepare_trace_presentation(trace)

    assert {row["Field"] for row in prepared["output_rows"]} == {
        "Commodity Index",
        "Target Unit Cost Usd",
        "Commodity",
    }
    assert prepared["intermediate_count"] == 0
    assert prepared["unresolved_count"] == 0
    assert prepared["technical_payload"]["raw_output"] is raw_output


def test_reconciliation_summary_explains_counts_and_retains_exact_arrays():
    item = {
        "exact_matches": ("$raw_output",),
        "tolerated_differences": (),
        "mismatches": (),
        "unavailable_evidence": (),
        "tolerance_rules": (),
    }

    prepared = prepare_reconciliation_presentation(item)

    assert prepared["rows"][0] == {
        "Evidence class": "Exact matches",
        "Count": 1,
        "Review meaning": "Authoritative and compared evidence align.",
    }
    assert prepared["review_required"] is False
    assert prepared["technical_payload"]["exact_matches"] == ("$raw_output",)


def test_reconciliation_flags_mismatch_or_unavailable_evidence_for_review():
    prepared = prepare_reconciliation_presentation({
        "exact_matches": (),
        "tolerated_differences": (),
        "mismatches": ("unit",),
        "unavailable_evidence": ("source",),
        "tolerance_rules": (),
    })

    assert prepared["review_required"] is True


def test_hosted_wrapper_uses_readable_evidence_renderers():
    source = Path("modules/calculation_explorer_currency_ui.py").read_text(encoding="utf-8")

    assert '"Calculation Trace": render_readable_trace' in source
    assert '"Reconciliation": render_readable_reconciliation' in source
    assert '"Calculation Trace": _render_trace' not in source
    assert '"Reconciliation": _render_reconciliation' not in source


def test_raw_evidence_remains_only_in_collapsed_technical_expanders():
    source = Path("modules/calculation_explorer_evidence_ui.py").read_text(encoding="utf-8")

    assert 'st.expander("Technical trace evidence", expanded=False)' in source
    assert 'st.expander("Technical reconciliation evidence", expanded=False)' in source
    assert "Exact governed trace payload retained for technical audit" in source
    assert "Exact reconciliation arrays retained for technical audit" in source
