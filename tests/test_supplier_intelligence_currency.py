"""Supplier Intelligence display-currency governance tests."""

from pathlib import Path

import pandas as pd

from modules.supplier_intelligence_currency_ui import (
    build_supplier_intelligence_currency_frames,
    build_supplier_intelligence_display_frame,
)


ROOT = Path(__file__).resolve().parents[1]
AUDIT_LABELS = {
    "Original Quote Currency",
    "Original Quote Unit Price",
    "Canonical Comparison Currency",
    "Canonical Comparison Unit Price",
    "FX Rate Used (INR/USD)",
    "Unit of Measure",
    "Canonical Comparison Basis",
}


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
            "Risk-Adjusted TCO (USD)": 1.50,
            "Risk Resilience Score": 80,
            "Performance Score": 75,
            "Supplier 360 Score": 82,
            "Recommendation Status": "Best value",
        }
    ])


def test_usd_mode_keeps_only_usd_business_values_in_main_frame():
    source = _comparison_frame()
    original = source.copy(deep=True)

    result = build_supplier_intelligence_display_frame(source, "USD", 83)

    assert result.loc[0, "Quoted Price (USD)"] == 1.25
    assert result.loc[0, "Risk-Adjusted TCO (USD)"] == 1.50
    assert "Quoted Price (INR)" not in result.columns
    assert not AUDIT_LABELS.intersection(result.columns)
    assert "Original Currency" not in result.columns
    assert "Normalized Unit Price" not in result.columns
    pd.testing.assert_frame_equal(source, original)


def test_inr_mode_derives_business_values_once_and_hides_all_usd_audit_fields():
    source = _comparison_frame()
    original = source.copy(deep=True)

    result = build_supplier_intelligence_display_frame(source, "INR", 83)

    assert "Quoted Price (USD)" not in result.columns
    assert "Risk-Adjusted TCO (USD)" not in result.columns
    assert result.loc[0, "Quoted Price (INR)"] == 103.75
    assert result.loc[0, "Risk-Adjusted TCO (INR)"] == 124.5
    assert "Original Currency" not in result.columns
    assert "Normalized Currency" not in result.columns
    assert "Comparison Basis" not in result.columns
    pd.testing.assert_frame_equal(source, original)


def test_both_mode_shows_separate_usd_and_inr_business_columns_only():
    result = build_supplier_intelligence_display_frame(_comparison_frame(), "Both", 83)

    assert result.loc[0, "Quoted Price (USD)"] == 1.25
    assert result.loc[0, "Quoted Price (INR)"] == 103.75
    assert result.loc[0, "Risk-Adjusted TCO (USD)"] == 1.50
    assert result.loc[0, "Risk-Adjusted TCO (INR)"] == 124.5
    assert "Normalized Unit Price" not in result.columns


def test_invalid_display_mode_falls_back_to_usd():
    result = build_supplier_intelligence_display_frame(_comparison_frame(), "INVALID", 83)

    assert "Quoted Price (USD)" in result.columns
    assert "Risk-Adjusted TCO (USD)" in result.columns
    assert "Quoted Price (INR)" not in result.columns


def test_precomputed_display_columns_are_rebuilt_without_duplicates_or_double_conversion():
    source = _comparison_frame()
    source["Quoted Price (USD)"] = 1.25
    source["Quoted Price (INR)"] = 103.75
    source["Risk-Adjusted TCO (INR)"] = 124.5

    result = build_supplier_intelligence_display_frame(source, "INR", 83)

    assert result.loc[0, "Quoted Price (INR)"] == 103.75
    assert result.loc[0, "Risk-Adjusted TCO (INR)"] == 124.5
    assert list(result.columns).count("Quoted Price (INR)") == 1
    assert list(result.columns).count("Risk-Adjusted TCO (INR)") == 1
    assert "Quoted Price (USD)" not in result.columns
    assert "Risk-Adjusted TCO (USD)" not in result.columns


def test_currency_audit_frame_preserves_original_and_canonical_metadata():
    business, audit = build_supplier_intelligence_currency_frames(_comparison_frame(), "INR", 83)

    assert "Original Currency" not in business.columns
    assert "Normalized Unit Price" not in business.columns
    assert audit.loc[0, "Supplier"] == "Supplier A"
    assert audit.loc[0, "Display Currency"] == "INR"
    assert audit.loc[0, "Original Quote Currency"] == "USD"
    assert audit.loc[0, "Original Quote Unit Price"] == 1.25
    assert audit.loc[0, "Canonical Comparison Currency"] == "USD"
    assert audit.loc[0, "Canonical Comparison Unit Price"] == 1.25
    assert audit.loc[0, "FX Rate Used (INR/USD)"] == 83.0
    assert audit.loc[0, "Unit of Measure"] == "piece"
    assert audit.loc[0, "Canonical Comparison Basis"] == "USD/piece"


def test_inr_business_columns_are_first_after_supplier_for_mobile_visibility():
    result = build_supplier_intelligence_display_frame(_comparison_frame(), "INR", 83)

    assert list(result.columns[:3]) == [
        "Supplier",
        "Quoted Price (INR)",
        "Risk-Adjusted TCO (INR)",
    ]


def test_both_mode_prioritizes_all_business_currency_columns():
    result = build_supplier_intelligence_display_frame(_comparison_frame(), "Both", 83)

    assert list(result.columns[:5]) == [
        "Supplier",
        "Quoted Price (USD)",
        "Risk-Adjusted TCO (USD)",
        "Quoted Price (INR)",
        "Risk-Adjusted TCO (INR)",
    ]


def test_app_passes_display_currency_and_fx_rate_to_supplier_intelligence():
    source = (ROOT / "app.py").read_text(encoding="utf-8")

    assert "from modules.supplier_intelligence_currency_ui import render_supplier_intelligence" in source
    assert "display_currency=display_currency" in source
    assert "fx_rate=fx_rate" in source


def test_currency_wrapper_delegates_audit_frame_without_bottom_expander():
    source = (ROOT / "modules" / "supplier_intelligence_currency_ui.py").read_text(encoding="utf-8")

    assert "currency_audit_df=audit_frame" in source
    assert "display_currency=mode" in source
    assert 'st.expander("Currency normalization and audit trail"' not in source
    assert "st.dataframe(audit_frame" not in source


def test_supplier_selector_and_recommendation_logic_remain_in_original_ui():
    source = (ROOT / "modules" / "supplier_intelligence_ui.py").read_text(encoding="utf-8")

    assert 'st.selectbox("Select Supplier 360 Profile"' in source
    assert 'render_comparison_matrix(recommendations, "Recommendation rankings")' in source
