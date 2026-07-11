import pandas as pd

from modules.exports import build_readable_supplier_scores, build_readable_supplier_comparison


def test_readable_supplier_scores_use_business_headings():
    df = pd.DataFrame([{
        "Supplier":"A",
        "Original Currency":"INR",
        "Original Unit Price":83.0,
        "Normalized Currency":"USD",
        "Normalized Unit Price":1.0,
        "FX Rate Used":83.0,
        "Unit of Measure":"kg",
        "Comparison Basis":"USD per kg",
        "adjusted_tco_unit_usd":1.1,
        "annual_tco_usd":1000,
        "risk_score":80,
        "risk_category":"Low",
        "performance_score":75,
        "esg_score":60,
        "supplier360_performance_score":72,
        "governed_financial_indicator":50,
        "governed_esg_maturity_score":55,
        "governed_innovation_maturity_score":50,
        "supplier360_score":70,
        "total_score":78,
    }])
    report = build_readable_supplier_scores(df, {"data_confidence_score":80,"confidence_category":"Acceptable With Review"}, {"status":"Eligible With Conditions","reason":"Review"})
    assert "Risk Resilience Score" in report.columns
    assert "Original Currency" in report.columns
    assert "Normalized Unit Price" in report.columns
    assert "Eligibility Status" in report.columns
    assert "RFQ Performance Score" in report.columns
    assert "RFQ ESG Score" in report.columns
    assert "Supplier 360 Performance Score" in report.columns
    assert "Governed ESG Maturity Score" in report.columns
    assert report.loc[0, "RFQ Performance Score"] == 75
    assert report.loc[0, "Supplier 360 Performance Score"] == 72
    assert report.loc[0, "RFQ ESG Score"] == 60
    assert report.loc[0, "Governed ESG Maturity Score"] == 55
    assert not any("_" in column for column in report.columns)


def test_readable_comparison_renames_risk_score():
    df = pd.DataFrame([{"Supplier":"A","Risk Score":80}])
    report = build_readable_supplier_comparison(df, {"data_confidence_score":80,"confidence_category":"Acceptable With Review"}, {"status":"Eligible","reason":"Passed"})
    assert "Risk Resilience Score" in report.columns
    assert "Risk Score" not in report.columns
