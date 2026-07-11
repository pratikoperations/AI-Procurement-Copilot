"""Regression tests for Build 0.9.5 Supplier Intelligence Platform."""

from modules.data_loader import get_demo_data
from modules.scoring import enrich_supplier_scores
from modules.supplier360_engine import build_supplier360_profile, build_supplier360_profiles
from modules.supplier_comparison import build_supplier_intelligence
from modules.supplier_esg_intelligence import evaluate_supplier_esg
from modules.supplier_financial_engine import evaluate_supplier_financial_health
from modules.supplier_innovation_engine import evaluate_supplier_innovation
from modules.supplier_performance_engine import evaluate_supplier_performance
from modules.supplier_recommendation_engine import generate_supplier_recommendations
from modules.srm_engine import classify_supplier_relationship

PACKAGING_ASSUMPTIONS = {
    "category": "Packaging Procurement",
    "commodity": "Corrugated Board",
    "annual_volume": 500000,
    "raw_material_shock": 0.0,
    "freight_shock": 0.0,
    "demand_change": 0.0,
}

RAW_ASSUMPTIONS = {
    "category": "Raw Material Procurement",
    "commodity": "PET Resin",
    "annual_volume": 500000,
    "raw_material_shock": 0.0,
    "freight_shock": 0.0,
    "demand_change": 0.0,
}


def _scored(category="Packaging Procurement"):
    assumptions = PACKAGING_ASSUMPTIONS if category == "Packaging Procurement" else RAW_ASSUMPTIONS
    return enrich_supplier_scores(get_demo_data(category, assumptions["commodity"]), assumptions)


def test_supplier360_profile_generation_is_complete():
    row = _scored().iloc[0].to_dict()
    profile = build_supplier360_profile(row, "Packaging Procurement", "Corrugated Board")
    assert profile["supplier_name"]
    assert 0 <= profile["overall_supplier360_score"] <= 100
    assert "performance" in profile and "financial" in profile and "esg" in profile and "innovation" in profile and "srm" in profile
    assert profile["data_note"]


def test_performance_scores_remain_in_range():
    result = evaluate_supplier_performance(_scored().iloc[0].to_dict())
    for key in ["quality_score", "delivery_score", "service_score", "commercial_score", "improvement_score", "overall_supplier_performance_score"]:
        assert 0 <= result[key] <= 100


def test_financial_health_is_indicator_not_bankruptcy_claim():
    result = evaluate_supplier_financial_health(_scored().iloc[0].to_dict())
    assert 0 <= result["financial_stability_score"] <= 100
    assert "not audited" in result["disclaimer"].lower()
    assert "bankruptcy" in result["disclaimer"].lower()


def test_esg_and_innovation_scores_remain_in_range():
    row = _scored().iloc[0].to_dict()
    esg = evaluate_supplier_esg(row)
    innovation = evaluate_supplier_innovation(row, "Packaging Procurement")
    assert 0 <= esg["esg_maturity_score"] <= 100
    assert 0 <= innovation["innovation_score"] <= 100


def test_srm_classification_is_supported():
    row = _scored().iloc[0].to_dict()
    performance = evaluate_supplier_performance(row)
    financial = evaluate_supplier_financial_health(row)
    esg = evaluate_supplier_esg(row)
    innovation = evaluate_supplier_innovation(row)
    result = classify_supplier_relationship(row, performance, financial, esg, innovation)
    assert result["srm_classification"] in {"Strategic", "Preferred", "Approved", "Transactional", "Development", "Exit Candidate"}


def test_recommendations_are_deterministic_and_explainable():
    profiles = build_supplier360_profiles(_scored(), "Packaging Procurement", "Corrugated Board")
    first = generate_supplier_recommendations(profiles)
    second = generate_supplier_recommendations(profiles)
    assert first == second
    assert len(first) == 10
    assert all(item["Explanation"] and "not black-box AI" in item["Governance"] for item in first)


def test_supplier_comparison_and_narrative_for_packaging():
    result = build_supplier_intelligence(_scored(), "Packaging Procurement", "Corrugated Board")
    assert len(result["comparison_df"]) == 3
    assert "Supplier 360 Score" in result["comparison_df"].columns
    assert "RECOMMENDATION" in result["executive_narrative"]


def test_supplier_intelligence_supports_raw_materials():
    result = build_supplier_intelligence(_scored("Raw Material Procurement"), "Raw Material Procurement", "PET Resin")
    assert len(result["profiles"]) == 3
    assert all(profile["approved_categories"] == "Raw Material Procurement" for profile in result["profiles"])
    assert result["comparison_df"]["Supplier 360 Score"].between(0, 100).all()
