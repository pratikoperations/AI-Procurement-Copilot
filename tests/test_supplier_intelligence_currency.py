"""Supplier Intelligence display-currency governance tests."""

from pathlib import Path

import pandas as pd

from modules.supplier_intelligence_currency_ui import build_supplier_intelligence_display_frame


ROOT = Path(__file__).resolve().parents[1]


def _comparison_frame():
    return pd.DataFrame([
        {
            "Supplier": "Supplier A",
            "Original Currency": "USD",
            "Original Unit Price": 1.25,
            "Normalized Currency": "USD",
            "Normalized Unit Price": 1.25,
            "FX Rate Used": 83.0,
            "Unit of Measure": "piece",
            "Comparison Basis": "USD/piece",
            "Quoted Price USD": 1.25,
            "Risk-Adjusted TCO USD": 1.50,
            "Risk Score": 80,
        }
    ])


def test_usd_mode_uses_usd_business_columns_and_preserves_metadata():
    source = _comparison_frame()
    original = source.copy(deep=True)

    result = build_supplier_intelligence_display_frame(source, "USD", 83)

    assert "Quoted Price (USD)" in result.columns
    assert "Risk-Adjusted TCO (USD)" in result.columns
    assert "Quoted Price (INR)" not in result.columns
    assert result.loc[0, "Quoted Price (USD)"] == 1.25
    assert result.loc[0, "Risk-Adjusted TCO (USD)"] == 1.50
    assert result.loc[0, "Original Currency"] == "USD"
    assert result.loc[0, "Normalized Currency"] == "USD"
    pd.testing.assert_frame_equal(source, original)


def test_inr_mode_converts_business_columns_once_and_hides_business_usd_columns():
    source = _comparison_frame()

    result = build_supplier_intelligence_display_frame(source, "INR", 83)

    assert "Quoted Price (USD)" not in result.columns
    assert "Risk-Adjusted TCO (USD)" not in result.columns
    assert result.loc[0, "Quoted Price (INR)"] == 103.75
    assert result.loc[0, "Risk-Adjusted TCO (INR)"] == 124.5
    assert result.loc[0, "Original Unit Price"] == 1.25
    assert result.loc[0, "Normalized Unit Price"] == 1.25
    assert result.loc[0, "FX Rate Used"] == 83.0


def test_both_mode_shows_separate_usd_and_inr_business_columns():
    result = build_supplier_intelligence_display_frame(_comparison_frame(), "Both", 83)

    assert result.loc[0, "Quoted Price (USD)"] == 1.25
    assert result.loc[0, "Quoted Price (INR)"] == 103.75
    assert result.loc[0, "Risk-Adjusted TCO (USD)"] == 1.50
    assert result.loc[0, "Risk-Adjusted TCO (INR)"] == 124.5


def test_invalid_display_mode_falls_back_to_usd():
    result = build_supplier_intelligence_display_frame(_comparison_frame(), "INVALID", 83)

    assert "Quoted Price (USD)" in result.columns
    assert "Risk-Adjusted TCO (USD)" in result.columns
    assert "Quoted Price (INR)" not in result.columns


def test_precomputed_inr_display_columns_are_not_double_converted():
    source = _comparison_frame()
    source["Quoted Price (INR)"] = 103.75
    source["Risk-Adjusted TCO (INR)"] = 124.5

    result = build_supplier_intelligence_display_frame(source, "INR", 83)

    assert result.loc[0, "Quoted Price (INR)"] == 103.75
    assert result.loc[0, "Risk-Adjusted TCO (INR)"] == 124.5
    assert list(result.columns).count("Quoted Price (INR)") == 1
    assert list(result.columns).count("Risk-Adjusted TCO (INR)") == 1


def test_app_passes_display_currency_and_fx_rate_to_supplier_intelligence():
    source = (ROOT / "app.py").read_text(encoding="utf-8")

    assert "from modules.supplier_intelligence_currency_ui import render_supplier_intelligence" in source
    assert "display_currency=display_currency" in source
    assert "fx_rate=fx_rate" in source


def test_supplier_selector_and_recommendation_logic_remain_in_original_ui():
    source = (ROOT / "modules" / "supplier_intelligence_ui.py").read_text(encoding="utf-8")

    assert 'st.selectbox("Select Supplier 360 Profile"' in source
    assert 'render_comparison_matrix(recommendations, "Recommendation rankings")' in source
