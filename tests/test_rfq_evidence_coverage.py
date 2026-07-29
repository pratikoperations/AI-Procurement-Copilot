from decimal import Decimal

import pytest

from modules.rfq_evidence_coverage import aggregate_event, aggregate_item, quotation_coverage


def complete():
    return {
        "REQUESTED_QUANTITY": 100,
        "QUOTED_QUANTITY": 100,
        "FULL_QUANTITY_AVAILABLE": True,
        "INCOTERMS_CODE": "DAP",
        "LEAD_TIME_DAYS": 10,
        "TECHNICALLY_APPROVED": True,
        "RISK_SCORE": 80,
        "ESG_SCORE": 70,
    }


def test_full_coverage_is_100():
    assert quotation_coverage(complete(), {"NORMALIZED_UNIT_PRICE": Decimal("10")}, has_history_match=True).coverage_percent == Decimal("100")


def test_missing_evidence_gets_zero_not_partial():
    assert quotation_coverage({}, {}, has_history_match=False).coverage_percent == 0


def test_item_uses_minimum_supplier_coverage():
    high = quotation_coverage(complete(), {"NORMALIZED_UNIT_PRICE": 1}, has_history_match=True)
    low = quotation_coverage({"REQUESTED_QUANTITY": 100, "QUOTED_QUANTITY": 100}, {"NORMALIZED_UNIT_PRICE": 1}, has_history_match=False)
    assert aggregate_item([high, low]).coverage_percent == low.coverage_percent


def test_event_quantity_weighted():
    high = quotation_coverage(complete(), {"NORMALIZED_UNIT_PRICE": 1}, has_history_match=True)
    low = quotation_coverage({}, {}, has_history_match=False)
    score, method = aggregate_event({"A": high, "B": low}, {"A": 100, "B": 300})
    assert method == "REQUESTED_QUANTITY_WEIGHTED" and score == Decimal("25")


@pytest.mark.parametrize("quantity", [None, 0, -1, "bad"])
def test_event_invalid_quantity_uses_disclosed_equal_fallback(quantity):
    coverage = quotation_coverage(complete(), {"NORMALIZED_UNIT_PRICE": 1}, has_history_match=True)
    assert aggregate_event({"A": coverage}, {"A": quantity})[1] == "EQUAL_ITEM_WEIGHTED_FALLBACK"


def test_technical_approval_false_does_not_receive_quality_credit():
    values = complete() | {"TECHNICALLY_APPROVED": False}
    coverage = quotation_coverage(values, {"NORMALIZED_UNIT_PRICE": 1}, has_history_match=True)
    assert coverage.dimension_results["quality"] is False


def test_technical_approval_true_receives_quality_credit():
    coverage = quotation_coverage(complete(), {"NORMALIZED_UNIT_PRICE": 1}, has_history_match=False)
    assert coverage.dimension_results["quality"] is True


@pytest.mark.parametrize("field,value", [("QUALITY_SCORE", -1), ("QUALITY_SCORE", 101), ("RISK_SCORE", -1), ("RISK_SCORE", 101), ("ESG_SCORE", -1), ("ESG_SCORE", 101)])
def test_invalid_score_ranges_receive_no_credit(field, value):
    values = complete()
    values["TECHNICALLY_APPROVED"] = False
    values[field] = value
    coverage = quotation_coverage(values, {"NORMALIZED_UNIT_PRICE": 1}, has_history_match=False)
    dimension = "quality" if field == "QUALITY_SCORE" else field.split("_")[0].lower()
    assert coverage.dimension_results[dimension] is False


def test_zero_commercial_charge_alone_is_not_evidence():
    values = {"FREIGHT_AMOUNT": 0}
    coverage = quotation_coverage(values, {}, has_history_match=False)
    assert coverage.dimension_results["commercial_terms"] is False


def test_valid_payment_term_is_commercial_evidence():
    coverage = quotation_coverage({"PAYMENT_TERMS_CODE": "Z030"}, {}, has_history_match=False)
    assert coverage.dimension_results["commercial_terms"] is True


def test_zero_day_lead_time_is_valid_delivery_evidence():
    coverage = quotation_coverage({"LEAD_TIME_DAYS": 0}, {}, has_history_match=False)
    assert coverage.dimension_results["delivery"] is True