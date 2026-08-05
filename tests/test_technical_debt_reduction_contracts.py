from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd
from hypothesis import given, settings, strategies as st

from modules.sourcemate_global_context import (
    GLOBAL_CONTEXT_CONTRACT,
    current_context,
    publish_scored_context,
    publish_selected_presentation,
)
from modules.ux_acceptance_corrections import build_contextual_currency_frame


@dataclass
class _FakeStreamlit:
    session_state: dict[str, Any] = field(default_factory=dict)


@given(
    amount=st.decimals(min_value="0", max_value="1000000", places=2, allow_nan=False, allow_infinity=False),
    fx_rate=st.decimals(min_value="1", max_value="200", places=4, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=40, deadline=None)
def test_currency_presentation_preserves_canonical_values_and_conversion_invariant(amount, fx_rate):
    canonical = pd.DataFrame({"Supplier": ["A"], "Quoted Unit Price USD": [float(amount)]})
    original = canonical.copy(deep=True)

    display = build_contextual_currency_frame(
        canonical,
        display_currency="INR",
        fx_rate=float(fx_rate),
    )

    pd.testing.assert_frame_equal(canonical, original)
    assert display.loc[0, "Quoted Unit Price (INR)"] == round(float(amount) * float(fx_rate), 2)


@given(display_currency=st.sampled_from(["USD", "INR", "Both"]))
def test_currency_surface_retains_non_currency_fields(display_currency):
    canonical = pd.DataFrame(
        {
            "Supplier": ["A"],
            "Rank": [1],
            "Quoted Unit Price USD": [12.5],
        }
    )

    display = build_contextual_currency_frame(canonical, display_currency=display_currency, fx_rate=83.25)

    assert display["Supplier"].tolist() == ["A"]
    assert display["Rank"].tolist() == [1]


def test_cross_surface_context_preserves_authority_and_evidence(monkeypatch):
    fake_st = _FakeStreamlit()
    monkeypatch.setattr("modules.sourcemate_global_context._st", lambda: fake_st)

    scored = pd.DataFrame(
        {
            "Supplier": ["Supplier A"],
            "Overall Score": [88.0],
            "Rank": [1],
            "Eligibility Status": ["Eligible"],
        }
    )
    publish_scored_context(
        scored,
        {
            "data_source": "Synthetic Demo",
            "category": "Packaging",
            "display_currency": "Both",
            "fx_rate": 83.25,
        },
    )
    publish_selected_presentation(
        {
            "calculation_overview": {"calculation_id": "CALC-1"},
            "calculation_trace": {"available": True, "trace_id": "TRACE-1"},
            "reconciliation": {"available": True, "classification": "exact"},
        }
    )

    context = current_context()

    assert context["contract_version"] == GLOBAL_CONTEXT_CONTRACT
    assert context["supplier_rows"][0]["supplier"] == "Supplier A"
    assert context["calculation_overview"]["calculation_id"] == "CALC-1"
    assert context["calculation_trace"]["trace_id"] == "TRACE-1"
    assert context["reconciliation"]["classification"] == "exact"
    assert context["human_review_required"] is True
    assert context["action_executed"] is False


def test_non_tabular_scored_context_fails_closed_and_emits_diagnostic(monkeypatch, caplog):
    fake_st = _FakeStreamlit()
    monkeypatch.setattr("modules.sourcemate_global_context._st", lambda: fake_st)

    with caplog.at_level("WARNING", logger="modules.sourcemate_global_context"):
        publish_scored_context(object(), {"data_source": "Synthetic Demo"})

    context = current_context()
    assert context["supplier_rows"] == []
    assert context["human_review_required"] is True
    assert context["action_executed"] is False
    assert any(
        getattr(record, "event", None) == "sourcemate_context_publish_fallback"
        for record in caplog.records
    )
