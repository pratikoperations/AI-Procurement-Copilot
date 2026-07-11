"""Build 0.9.6 business-rule validation tests."""

import pandas as pd

from modules.business_rule_validator import validate_business_rules


def _base_df():
    return pd.DataFrame([
        {"Supplier":"A","Quoted Unit Price USD":1.0,"MOQ":100,"Lead Time Days":10,"Currency":"USD","Unit":"kg","OTIF %":95,"Audit Score":85,"Quality PPM":500,"Complaint Rate %":1,"Supplier Capacity":700},
        {"Supplier":"B","Quoted Unit Price USD":1.1,"MOQ":100,"Lead Time Days":12,"Currency":"USD","Unit":"kg","OTIF %":92,"Audit Score":82,"Quality PPM":700,"Complaint Rate %":2,"Supplier Capacity":500},
    ])


def test_valid_rules_pass():
    allocation = pd.DataFrame([
        {"Supplier":"A","Recommended Allocation %":60},
        {"Supplier":"B","Recommended Allocation %":40},
    ])
    result = validate_business_rules(_base_df(), 1000, allocation)
    assert result["status"] in {"Pass", "Warning"}
    assert not result["blocking_issues"]


def test_negative_price_blocks():
    df = _base_df()
    df.loc[0, "Quoted Unit Price USD"] = -1
    result = validate_business_rules(df, 1000)
    assert result["status"] == "Fail"
    assert any("greater than zero" in issue for issue in result["blocking_issues"])


def test_mixed_currency_blocks():
    df = _base_df()
    df.loc[1, "Currency"] = "INR"
    result = validate_business_rules(df, 1000)
    assert any("Mixed currencies" in issue for issue in result["blocking_issues"])


def test_capacity_shortfall_and_bad_allocation_block():
    allocation = pd.DataFrame([
        {"Supplier":"A","Recommended Allocation %":80},
        {"Supplier":"B","Recommended Allocation %":10},
    ])
    result = validate_business_rules(_base_df(), 1500, allocation)
    assert result["status"] == "Fail"
    assert any("below annual demand" in issue for issue in result["blocking_issues"])
    assert any("instead of 100" in issue for issue in result["blocking_issues"])


def test_out_of_range_percentage_blocks():
    df = _base_df()
    df.loc[0, "OTIF %"] = 110
    result = validate_business_rules(df, 1000)
    assert any("between 0 and 100" in issue for issue in result["blocking_issues"])
