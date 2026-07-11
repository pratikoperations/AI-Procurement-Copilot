"""Adversarial and boundary tests for Build 0.9.6."""

import pandas as pd

from modules.business_rule_validator import validate_business_rules
from modules.data_confidence import calculate_data_confidence
from modules.recommendation_eligibility import evaluate_recommendation_eligibility


def _df():
    return pd.DataFrame([
        {"Supplier":"A","Quoted Unit Price USD":1.0,"MOQ":100,"Lead Time Days":10,"Payment Terms":"Net 30","Incoterms":"DDP","Currency":"USD","Unit":"kg","OTIF %":95,"Audit Score":85,"Quality PPM":500,"Complaint Rate %":1,"Supplier Capacity":600},
        {"Supplier":"B","Quoted Unit Price USD":1.1,"MOQ":100,"Lead Time Days":12,"Payment Terms":"Net 45","Incoterms":"DDP","Currency":"USD","Unit":"kg","OTIF %":90,"Audit Score":80,"Quality PPM":700,"Complaint Rate %":2,"Supplier Capacity":500},
    ])


def test_zero_volume_blocks():
    rules = validate_business_rules(_df(), 0)
    assert rules["status"] == "Fail"
    assert any("Annual volume" in issue for issue in rules["blocking_issues"])


def test_single_supplier_is_warning_not_silent_high_confidence():
    df = _df().iloc[[0]].copy()
    confidence = calculate_data_confidence(df)
    rules = validate_business_rules(df, 500)
    result = evaluate_recommendation_eligibility(
        {"is_valid":True,"warnings":["At least two suppliers are recommended"]},
        rules,
        confidence,
        pd.DataFrame([{"Supplier":"A","risk_score":80}]),
        500,
        50,
    )
    assert result["status"] in {"Eligible With Conditions", "Human Review Required"}


def test_decimal_percentage_is_flagged():
    df = _df()
    df.loc[0, "OTIF %"] = 0.95
    rules = validate_business_rules(df, 1000)
    assert any("decimal percentages" in issue for issue in rules["non_blocking_issues"])


def test_mixed_units_block():
    df = _df()
    df.loc[1, "Unit"] = "piece"
    rules = validate_business_rules(df, 1000)
    assert any("Mixed units" in issue for issue in rules["blocking_issues"])


def test_allocation_capacity_exceedance_blocks():
    allocation = pd.DataFrame([
        {"Supplier":"A","Recommended Allocation %":80},
        {"Supplier":"B","Recommended Allocation %":20},
    ])
    rules = validate_business_rules(_df(), 1000, allocation)
    assert any("requires" in issue and "capacity" in issue for issue in rules["blocking_issues"])


def test_missing_critical_data_is_insufficient_or_blocked():
    df = _df().drop(columns=["Quoted Unit Price USD", "Payment Terms"])
    confidence = calculate_data_confidence(df)
    assert confidence["missing_critical_data_percentage"] > 0
    assert confidence["confidence_category"] in {"Limited Confidence", "Insufficient Data"}
