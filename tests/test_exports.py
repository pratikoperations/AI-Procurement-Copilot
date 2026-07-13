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
    source = pd.DataFrame([{
        "Supplier": "A",
        "Risk Score": 80,
        "Risk-Adjusted TCO (USD)": 2.0,
        "Original Currency": "INR",
        "Normalized Currency": "USD",
    }])
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
    source = pd.DataFrame([{
        "Supplier": "A",
        "Recommended Allocation %": 100,
        "Estimated Annual TCO USD": 1000.0,
        "Estimated Annual TCO INR": 999999.0,
    }])
    usd = build_readable_allocation(source, "USD", 83)
    inr = build_readable_allocation(source, "INR", 83)
    both = build_readable_allocation(source, "Both", 83)
    assert list(column for column in usd.columns if "Estimated Annual TCO" in column) == ["Estimated Annual TCO (USD)"]
    assert inr.loc[0, "Estimated Annual TCO (INR)"] == 83000.0
    assert both.loc[0, "Estimated Annual TCO (USD)"] == 1000.0
    assert both.loc[0, "Estimated Annual TCO (INR)"] == 83000.0
    assert source.loc[0, "Estimated Annual TCO INR"] == 999999.0


def test_should_cost_and_scenarios_support_all_display_modes():
    should_cost = pd.DataFrame([{"Component": "Resin", "Unit Cost USD": 2.0, "Annual Impact USD": 1000.0, "Annual Impact INR": 1.0}])
    scenario = pd.DataFrame([{"Scenario": "Base", "Winning Supplier": "A", "Annual TCO (USD)": 1000.0}])
    should_inr = build_readable_should_cost(should_cost, "INR", 83)
    scenario_both = build_readable_scenarios(scenario, "Both", 83)
    assert should_inr.loc[0, "Unit Cost (INR)"] == 166.0
    assert should_inr.loc[0, "Annual Impact (INR)"] == 83000.0
    assert scenario_both.loc[0, "Annual TCO (USD)"] == 1000.0
    assert scenario_both.loc[0, "Annual TCO (INR)"] == 83000.0


def test_excel_readable_sheets_follow_currency_and_audit_sheet_stays_canonical():
    scored = _scores()
    should_cost = pd.DataFrame([{"Component": "Resin", "Unit Cost USD": 2.0}])
    allocation = pd.DataFrame([{"Supplier": "A", "Recommended Allocation %": 100, "Estimated Annual TCO USD": 1000.0}])
    scenarios = pd.DataFrame([{"Scenario": "Base", "Winning Supplier": "A", "Annual TCO (USD)": 1000.0}])
    readable_scores = build_readable_supplier_scores(scored, CONFIDENCE, ELIGIBILITY, display_currency="INR", fx_rate=83)
    readable_comparison = build_readable_supplier_comparison(
        pd.DataFrame([{"Supplier": "A", "Risk-Adjusted TCO (USD)": 2.0}]),
        CONFIDENCE,
        ELIGIBILITY,
        "INR",
        83,
    )
    workbook = build_excel_workbook(
        scored,
        should_cost,
        allocation,
        scenarios,
        readable_scores,
        readable_comparison,
        display_currency="INR",
        fx_rate=83,
    )
    sheets = pd.read_excel(io.BytesIO(workbook), sheet_name=None)
    assert "Annual TCO (INR)" in sheets["Supplier Scores Report"].columns
    assert "Risk-Adjusted TCO (INR)" in sheets["Supplier Comparison"].columns
    assert "Unit Cost (INR)" in sheets["Should Cost"].columns
    assert "Estimated Annual TCO (INR)" in sheets["Allocation"].columns
    assert "Annual TCO (INR)" in sheets["Scenarios"].columns
    assert "annual_tco_usd" in sheets["Audit Supplier Scores"].columns
    assert sheets["Audit Supplier Scores"].loc[0, "annual_tco_usd"] == 1000.0


def test_json_audit_payload_is_display_mode_independent():
    scored = _scores()
    allocation = pd.DataFrame([{"Supplier": "A", "Estimated Annual TCO USD": 1000.0}])
    scenarios = pd.DataFrame([{"Scenario": "Base", "Annual TCO (USD)": 1000.0}])
    payload_a = build_decision_package_json(scored.iloc[0], {"value_usd": 10}, allocation, scenarios, {"annual_saving_usd": 5})
    payload_b = build_decision_package_json(scored.iloc[0], {"value_usd": 10}, allocation, scenarios, {"annual_saving_usd": 5})
    assert json.loads(payload_a.decode("utf-8")) == json.loads(payload_b.decode("utf-8"))
