import io
import json

import pandas as pd

from modules.exports import (
    build_decision_package_json,
    build_excel_workbook,
    build_readable_allocation,
    build_readable_scenarios,
    build_readable_should_cost,
    build_readable_supplier_comparison,
    build_readable_supplier_scores,
)


CONFIDENCE = {"data_confidence_score": 80, "confidence_category": "Acceptable With Review"}
ELIGIBILITY = {"status": "Eligible With Conditions", "reason": "Review"}


def _scores():
    return pd.DataFrame([{
        "Supplier": "A",
        "Original Currency": "INR",
        "Original Unit Price": 83.0,
        "Normalized Currency": "USD",
        "Normalized Unit Price": 1.0,
        "FX Rate Used": 83.0,
        "Unit of Measure": "kg",
        "Comparison Basis": "USD per kg",
        "adjusted_tco_unit_usd": 1.1,
        "annual_tco_usd": 1000.0,
        "risk_score": 80,
        "risk_category": "Low",
        "performance_score": 75,
        "esg_score": 60,
        "supplier360_performance_score": 72,
        "governed_financial_indicator": 50,
        "governed_esg_maturity_score": 55,
        "governed_innovation_maturity_score": 50,
        "supplier360_score": 70,
        "total_score": 78,
    }])


def _should_cost():
    return pd.DataFrame([{
        "Component": "Resin",
        "Unit Cost USD": 2.0,
        "Annual Impact USD": 1000.0,
        "Annual Impact INR": 999999.0,
    }])


def _scenarios():
    return pd.DataFrame([{
        "Scenario": "Base",
        "Winning Supplier": "A",
        "Annual TCO (USD)": 1000.0,
    }])


def _allocation():
    return pd.DataFrame([{
        "Supplier": "A",
        "Recommended Allocation %": 100,
        "Estimated Annual TCO USD": 1000.0,
        "Estimated Annual TCO INR": 999999.0,
    }])


def _comparison():
    return pd.DataFrame([{
        "Supplier": "A",
        "Risk Score": 80,
        "Risk-Adjusted TCO (USD)": 2.0,
        "Original Currency": "INR",
        "Normalized Currency": "USD",
    }])


def _read_workbook(mode="USD", fx_rate=83):
    scored = _scores()
    readable_scores = build_readable_supplier_scores(
        scored,
        CONFIDENCE,
        ELIGIBILITY,
        display_currency=mode,
        fx_rate=fx_rate,
    )
    readable_comparison = build_readable_supplier_comparison(
        _comparison(),
        CONFIDENCE,
        ELIGIBILITY,
        display_currency=mode,
        fx_rate=fx_rate,
    )
    workbook = build_excel_workbook(
        scored,
        _should_cost(),
        _allocation(),
        _scenarios(),
        readable_scores,
        readable_comparison,
        display_currency=mode,
        fx_rate=fx_rate,
    )
    return pd.read_excel(io.BytesIO(workbook), sheet_name=None)


def _assert_audit_sheet_is_canonical(sheets):
    audit = sheets["Audit Supplier Scores"]
    assert "annual_tco_usd" in audit.columns
    assert "adjusted_tco_unit_usd" in audit.columns
    assert audit.loc[0, "annual_tco_usd"] == 1000.0
    assert audit.loc[0, "adjusted_tco_unit_usd"] == 1.1


def test_readable_supplier_scores_use_business_headings_and_default_usd():
    report = build_readable_supplier_scores(_scores(), CONFIDENCE, ELIGIBILITY)
    assert "Risk Resilience Score" in report.columns
    assert "Risk-Adjusted TCO (USD)" in report.columns
    assert "Annual TCO (USD)" in report.columns
    assert report.loc[0, "Annual TCO (USD)"] == 1000.0
    assert report.loc[0, "Normalized Currency"] == "USD"
    assert report.loc[0, "Comparison Basis"] == "USD per kg"
    assert not any("_" in column for column in report.columns)


def test_readable_supplier_scores_inr_and_both_modes_do_not_mutate_source():
    source = _scores()
    original = source.copy(deep=True)
    inr = build_readable_supplier_scores(source, CONFIDENCE, ELIGIBILITY, display_currency="INR", fx_rate=83)
    both = build_readable_supplier_scores(source, CONFIDENCE, ELIGIBILITY, display_currency="Both", fx_rate=83)
    assert "Annual TCO (USD)" not in inr.columns
    assert inr.loc[0, "Annual TCO (INR)"] == 83000.0
    assert both.loc[0, "Risk-Adjusted TCO (USD)"] == 1.1
    assert both.loc[0, "Risk-Adjusted TCO (INR)"] == 91.3
    assert both.loc[0, "Normalized Currency"] == "USD"
    pd.testing.assert_frame_equal(source, original)


def test_readable_comparison_supports_all_display_modes():
    source = _comparison()
    usd = build_readable_supplier_comparison(source, CONFIDENCE, ELIGIBILITY)
    inr = build_readable_supplier_comparison(source, CONFIDENCE, ELIGIBILITY, "INR", 83)
    both = build_readable_supplier_comparison(source, CONFIDENCE, ELIGIBILITY, "Both", 83)
    assert "Risk Resilience Score" in usd.columns
    assert usd.loc[0, "Risk-Adjusted TCO (USD)"] == 2.0
    assert inr.loc[0, "Risk-Adjusted TCO (INR)"] == 166.0
    assert "Risk-Adjusted TCO (USD)" in both.columns
    assert "Risk-Adjusted TCO (INR)" in both.columns
    assert both.loc[0, "Normalized Currency"] == "USD"


def test_readable_allocation_supports_usd_inr_both_without_double_conversion():
    source = _allocation()
    usd = build_readable_allocation(source, "USD", 83)
    inr = build_readable_allocation(source, "INR", 83)
    both = build_readable_allocation(source, "Both", 83)
    assert list(column for column in usd.columns if "Estimated Annual TCO" in column) == ["Estimated Annual TCO (USD)"]
    assert inr.loc[0, "Estimated Annual TCO (INR)"] == 83000.0
    assert both.loc[0, "Estimated Annual TCO (USD)"] == 1000.0
    assert both.loc[0, "Estimated Annual TCO (INR)"] == 83000.0
    assert source.loc[0, "Estimated Annual TCO INR"] == 999999.0


def test_should_cost_usd_mode_preserves_canonical_values():
    source = _should_cost()
    original = source.copy(deep=True)

    result = build_readable_should_cost(source, "USD", 83)

    assert result.loc[0, "Unit Cost (USD)"] == 2.0
    assert result.loc[0, "Annual Impact (USD)"] == 1000.0
    assert "Unit Cost (INR)" not in result.columns
    assert "Annual Impact (INR)" not in result.columns
    pd.testing.assert_frame_equal(source, original)


def test_should_cost_inr_mode_converts_from_usd_once():
    source = _should_cost()

    result = build_readable_should_cost(source, "INR", 83)

    assert "Unit Cost (USD)" not in result.columns
    assert "Annual Impact (USD)" not in result.columns
    assert result.loc[0, "Unit Cost (INR)"] == 166.0
    assert result.loc[0, "Annual Impact (INR)"] == 83000.0
    assert result.loc[0, "Annual Impact (INR)"] != 999999.0


def test_should_cost_both_mode_has_both_currencies_without_double_conversion():
    source = _should_cost()
    original = source.copy(deep=True)

    result = build_readable_should_cost(source, "Both", 83)

    assert result.loc[0, "Unit Cost (USD)"] == 2.0
    assert result.loc[0, "Unit Cost (INR)"] == 166.0
    assert result.loc[0, "Annual Impact (USD)"] == 1000.0
    assert result.loc[0, "Annual Impact (INR)"] == 83000.0
    pd.testing.assert_frame_equal(source, original)


def test_scenarios_usd_mode_preserves_canonical_value():
    source = _scenarios()
    original = source.copy(deep=True)

    result = build_readable_scenarios(source, "USD", 83)

    assert result.loc[0, "Annual TCO (USD)"] == 1000.0
    assert "Annual TCO (INR)" not in result.columns
    pd.testing.assert_frame_equal(source, original)


def test_scenarios_inr_mode_converts_correctly():
    result = build_readable_scenarios(_scenarios(), "INR", 83)

    assert "Annual TCO (USD)" not in result.columns
    assert result.loc[0, "Annual TCO (INR)"] == 83000.0


def test_scenarios_both_mode_has_both_currencies_and_preserves_source():
    source = _scenarios()
    original = source.copy(deep=True)

    result = build_readable_scenarios(source, "Both", 83)

    assert result.loc[0, "Annual TCO (USD)"] == 1000.0
    assert result.loc[0, "Annual TCO (INR)"] == 83000.0
    pd.testing.assert_frame_equal(source, original)


def test_excel_workbook_usd_mode_uses_usd_readable_columns_and_canonical_audit():
    sheets = _read_workbook("USD")

    assert "Annual TCO (USD)" in sheets["Supplier Scores Report"].columns
    assert "Risk-Adjusted TCO (USD)" in sheets["Supplier Comparison"].columns
    assert "Unit Cost (USD)" in sheets["Should Cost"].columns
    assert "Estimated Annual TCO (USD)" in sheets["Allocation"].columns
    assert "Annual TCO (USD)" in sheets["Scenarios"].columns
    _assert_audit_sheet_is_canonical(sheets)


def test_excel_workbook_inr_mode_uses_only_inr_readable_columns_and_canonical_audit():
    sheets = _read_workbook("INR")

    governed_columns = {
        "Supplier Scores Report": ("Annual TCO (INR)", "Annual TCO (USD)"),
        "Supplier Comparison": ("Risk-Adjusted TCO (INR)", "Risk-Adjusted TCO (USD)"),
        "Should Cost": ("Unit Cost (INR)", "Unit Cost (USD)"),
        "Allocation": ("Estimated Annual TCO (INR)", "Estimated Annual TCO (USD)"),
        "Scenarios": ("Annual TCO (INR)", "Annual TCO (USD)"),
    }
    for sheet_name, (inr_column, usd_column) in governed_columns.items():
        assert inr_column in sheets[sheet_name].columns
        assert usd_column not in sheets[sheet_name].columns
    _assert_audit_sheet_is_canonical(sheets)


def test_excel_workbook_both_mode_uses_both_readable_columns_and_canonical_audit():
    sheets = _read_workbook("Both")

    expected_pairs = {
        "Supplier Scores Report": ("Annual TCO (USD)", "Annual TCO (INR)"),
        "Supplier Comparison": ("Risk-Adjusted TCO (USD)", "Risk-Adjusted TCO (INR)"),
        "Should Cost": ("Unit Cost (USD)", "Unit Cost (INR)"),
        "Allocation": ("Estimated Annual TCO (USD)", "Estimated Annual TCO (INR)"),
        "Scenarios": ("Annual TCO (USD)", "Annual TCO (INR)"),
    }
    for sheet_name, (usd_column, inr_column) in expected_pairs.items():
        assert usd_column in sheets[sheet_name].columns
        assert inr_column in sheets[sheet_name].columns
    _assert_audit_sheet_is_canonical(sheets)


def test_excel_workbook_default_currency_is_usd():
    scored = _scores()
    workbook = build_excel_workbook(
        scored,
        _should_cost(),
        _allocation(),
        _scenarios(),
    )
    sheets = pd.read_excel(io.BytesIO(workbook), sheet_name=None)

    assert "Annual TCO (USD)" in sheets["Supplier Scores Report"].columns
    assert "Unit Cost (USD)" in sheets["Should Cost"].columns
    assert "Estimated Annual TCO (USD)" in sheets["Allocation"].columns
    assert "Annual TCO (USD)" in sheets["Scenarios"].columns
    _assert_audit_sheet_is_canonical(sheets)


def test_json_audit_builder_has_no_display_currency_dependency_and_preserves_usd_fields():
    scored = _scores()
    allocation = pd.DataFrame([{"Supplier": "A", "Estimated Annual TCO USD": 1000.0}])
    scenarios = pd.DataFrame([{"Scenario": "Base", "Annual TCO (USD)": 1000.0}])

    payload = build_decision_package_json(
        scored.iloc[0],
        {"value_usd": 10},
        allocation,
        scenarios,
        {"annual_saving_usd": 5},
    )
    decoded = json.loads(payload.decode("utf-8"))

    assert decoded["recommended_supplier"]["annual_tco_usd"] == 1000.0
    assert decoded["recommended_supplier"]["adjusted_tco_unit_usd"] == 1.1
    assert decoded["allocation"][0]["Estimated Annual TCO USD"] == 1000.0
    assert decoded["scenarios"][0]["Annual TCO (USD)"] == 1000.0
    assert decoded["value_metrics"]["value_usd"] == 10
    assert decoded["negotiation"]["annual_saving_usd"] == 5
