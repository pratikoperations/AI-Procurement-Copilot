from pathlib import Path
from types import SimpleNamespace

import pandas as pd

from modules.rfq_handoff_models import EngineStageResult
from modules.rfq_legacy_compatibility import (
    GOVERNED_RANKING_INPUTS_NOT_CANONICAL,
    assess_legacy_compatibility,
)
from modules.rfq_review_ui import _field_label, _unit_price


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


def test_review_ui_preserves_normalization_evidence_and_unit_columns():
    source = Path("modules/rfq_review_ui.py").read_text(encoding="utf-8")
    for label in (
        "FX Rate",
        "FX Date",
        "Source UOM",
        "Comparison UOM",
        "Evidence %",
        "History Match",
        "Source Unit Price",
        "Normalized Unit Price",
    ):
        assert f'"{label}"' in source
    assert "currency and unit of measure" in source


def test_streamlit_review_does_not_render_raw_code_or_json():
    review_source = Path("modules/rfq_review_ui.py").read_text(encoding="utf-8")
    app_source = Path("app.py").read_text(encoding="utf-8")
    assert "st.code(" not in review_source
    assert "st.json(" not in review_source
    assert "st.json(" not in app_source
    assert "Confirmation reference:" in review_source
    assert "full technical fingerprint is retained internally" in review_source


def test_stage_audit_exposes_only_business_safe_labels():
    result = EngineStageResult(
        "SCORING_TCO",
        "BLOCKED",
        "secret-digest",
        ("S1", "S2"),
        "SCORING_TCO_FAILED",
        "Supplier scoring could not be completed.",
    )
    row = result.__dict__
    assert row == {
        "Stage": "Supplier scoring and total cost",
        "Status": "Stopped",
        "Suppliers": "S1, S2",
        "Details": "Supplier scoring could not be completed.",
    }
    assert "secret-digest" not in str(row)
    assert "SCORING_TCO" not in str(row)
    assert result.stage == "SCORING_TCO"
    assert result.input_digest == "secret-digest"


def test_common_ranking_fields_show_required_units():
    assert _field_label("OTIF_PERCENT") == "OTIF (%)"
    assert _field_label("QUALITY_PPM") == "Quality (ppm)"
    assert _field_label("PCR_CONTENT_PERCENT") == "PCR content (%)"
    assert _field_label("SUPPLIER_AUDIT_SCORE") == "Supplier audit score (0–100)"


def test_unit_price_combines_currency_value_and_uom():
    assert _unit_price(12.5, "USD", "KG") == "USD 12.5 / kg"
    assert _unit_price(83, "INR", "EA") == "INR 83 / ea"


def test_app_preserves_public_navigation_and_claim_safety_structure():
    source = Path("app.py").read_text(encoding="utf-8")
    assert 'st.selectbox(\n    "Explore the sourcing workflow"' in source
    assert "This application supports human procurement review" in source
    assert "does not claim production deployment" in source
    assert "sections = [\n" in source
    assert "render_handoff_confirmation" in source
    assert "run_engine_stages" in source
