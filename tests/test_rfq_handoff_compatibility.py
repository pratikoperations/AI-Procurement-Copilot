from types import SimpleNamespace

import pandas as pd

from modules.rfq_legacy_compatibility import (
    GOVERNED_RANKING_INPUTS_NOT_CANONICAL,
    assess_legacy_compatibility,
)


def _orchestration():
    quote = SimpleNamespace(
        eligible_for_analysis=True,
        record=SimpleNamespace(
            canonical_values={"RFQ_NUMBER": "RFQ1", "RFQ_ITEM": "10"},
            provenance=SimpleNamespace(source_row_id="Q1"),
        ),
        normalization=SimpleNamespace(normalized_values={"COMPARISON_CURRENCY": "USD", "NORMALIZED_UNIT_PRICE": 10}),
    )
    quote2 = SimpleNamespace(
        eligible_for_analysis=True,
        record=SimpleNamespace(
            canonical_values={"RFQ_NUMBER": "RFQ1", "RFQ_ITEM": "10"},
            provenance=SimpleNamespace(source_row_id="Q2"),
        ),
        normalization=SimpleNamespace(normalized_values={"COMPARISON_CURRENCY": "USD", "NORMALIZED_UNIT_PRICE": 11}),
    )
    return SimpleNamespace(enriched_quotes=(quote, quote2))


def test_review_only_compatibility_retains_ranking_blocker():
    result = assess_legacy_compatibility(_orchestration(), selected_rfq_number="RFQ1", selected_rfq_item="10")
    assert not result.compatible
    assert result.dataframe is None
    assert GOVERNED_RANKING_INPUTS_NOT_CANONICAL in result.blockers


def test_machine_ready_unconfirmed_requires_digest_confirmation():
    frame = pd.DataFrame({"Supplier": ["A", "B"]})
    handoff = SimpleNamespace(eligible=True, dataframe=frame, blockers=(), digest="abc")
    result = assess_legacy_compatibility(_orchestration(), selected_rfq_number="RFQ1", selected_rfq_item="10", handoff_result=handoff, handoff_confirmed=False)
    assert not result.compatible
    assert result.dataframe is None
    assert GOVERNED_RANKING_INPUTS_NOT_CANONICAL not in result.blockers
    assert "ANALYTICAL_HANDOFF_CONFIRMATION_REQUIRED" in result.blockers


def test_confirmed_handoff_returns_only_governed_dataframe():
    frame = pd.DataFrame({"Supplier": ["A", "B"]})
    handoff = SimpleNamespace(eligible=True, dataframe=frame, blockers=(), digest="abc")
    result = assess_legacy_compatibility(_orchestration(), selected_rfq_number="RFQ1", selected_rfq_item="10", handoff_result=handoff, handoff_confirmed=True)
    assert result.compatible
    assert result.dataframe is frame
    assert result.blockers == ()
    assert result.handoff_digest == "abc"
