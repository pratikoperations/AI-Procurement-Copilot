"""Evidence-governance regression tests for Build 0.9.6.1."""

from modules.supplier_esg_intelligence import evaluate_supplier_esg
from modules.supplier_financial_engine import evaluate_supplier_financial_health
from modules.supplier_innovation_engine import evaluate_supplier_innovation


def test_financial_score_is_capped_when_evidence_is_missing():
    result = evaluate_supplier_financial_health({"Payment Terms": "Net 60", "Capacity Buffer %": 20})
    assert result["assessment_status"] == "Insufficient Data"
    assert result["displayed_financial_score"] <= 50
    assert result["due_diligence_required"] is True
    assert result["raw_indicator_score"] >= result["displayed_financial_score"]
    assert result["financial_risk_category"] == "Due Diligence Required"


def test_financial_limited_evidence_is_provisional_and_capped():
    result = evaluate_supplier_financial_health({
        "Capacity Utilization %": 70,
        "Payment Terms": "Net 45",
    })
    assert result["assessment_status"] == "Insufficient Data" or result["assessment_status"] == "Limited Evidence"
    assert result["displayed_financial_score"] <= 70


def test_esg_low_evidence_cannot_be_advanced_or_leading():
    result = evaluate_supplier_esg({"Recyclability": 95, "Carbon Score": 95})
    assert result["assessment_status"] == "Insufficient Data"
    assert result["displayed_esg_score"] <= 50
    assert result["esg_maturity_level"] not in {"Leading", "Advanced"}
    assert result["verification_required"] is True


def test_innovation_low_evidence_cannot_exceed_basic():
    result = evaluate_supplier_innovation({"Design Capability Score": 95})
    assert result["assessment_status"] == "Insufficient Data"
    assert result["displayed_innovation_score"] <= 50
    assert result["innovation_maturity_level"] in {"Basic", "Low"}
    assert result["verification_required"] is True


def test_complete_evidence_preserves_raw_scores():
    financial = evaluate_supplier_financial_health({
        "Capacity Utilization %": 70,
        "Buyer Dependency %": 10,
        "Revenue Concentration %": 20,
        "Payment Terms": "Net 60",
    })
    assert financial["assessment_status"] == "Sufficient Evidence"
    assert financial["displayed_financial_score"] == financial["raw_indicator_score"]
