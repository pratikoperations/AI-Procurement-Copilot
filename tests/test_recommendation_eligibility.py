"""Build 0.9.6 recommendation eligibility tests."""

import pandas as pd

from modules.recommendation_eligibility import evaluate_recommendation_eligibility


SCORED = pd.DataFrame([{"Supplier":"A","risk_score":80}])


def test_blocking_rules_block_recommendation():
    result = evaluate_recommendation_eligibility(
        {"is_valid":True,"warnings":[]},
        {"blocking_issues":["Negative price"],"non_blocking_issues":[]},
        {"data_confidence_score":90,"confidence_category":"High Confidence"},
        SCORED,
        1000,
        50,
    )
    assert result["status"] == "Blocked"
    assert result["recommendation_allowed"] is False
    assert result["final_award_language_allowed"] is False


def test_low_confidence_requires_human_review():
    result = evaluate_recommendation_eligibility(
        {"is_valid":True,"warnings":[]},
        {"blocking_issues":[],"non_blocking_issues":[]},
        {"data_confidence_score":60,"confidence_category":"Limited Confidence"},
        SCORED,
        1000,
        50,
    )
    assert result["status"] == "Human Review Required"
    assert result["recommendation_allowed"] is True
    assert result["final_award_language_allowed"] is False


def test_strong_clean_data_is_eligible():
    result = evaluate_recommendation_eligibility(
        {"is_valid":True,"warnings":[]},
        {"blocking_issues":[],"non_blocking_issues":[]},
        {"data_confidence_score":90,"confidence_category":"High Confidence"},
        SCORED,
        1000,
        50,
    )
    assert result["status"] == "Eligible"
    assert result["final_award_language_allowed"] is True


def test_no_supplier_meets_risk_threshold_blocks():
    result = evaluate_recommendation_eligibility(
        {"is_valid":True,"warnings":[]},
        {"blocking_issues":[],"non_blocking_issues":[]},
        {"data_confidence_score":90,"confidence_category":"High Confidence"},
        pd.DataFrame([{"Supplier":"A","risk_score":30}]),
        1000,
        60,
    )
    assert result["status"] == "Blocked"
    assert any("risk-score threshold" in issue for issue in result["failed_checks"])
