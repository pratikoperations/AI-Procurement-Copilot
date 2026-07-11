from modules.supplier_recommendation_engine import generate_supplier_recommendations


def _profile(name, score, financial_status="Insufficient Data", esg_status="Insufficient Data", innovation_status="Insufficient Data", classification="Preferred"):
    return {
        "supplier_name": name,
        "overall_supplier360_score": score,
        "performance": {"overall_supplier_performance_score": score},
        "financial": {"displayed_financial_score": 50, "assessment_status": financial_status},
        "esg": {"displayed_esg_score": 50, "assessment_status": esg_status, "esg_data_completeness": 0},
        "innovation": {"displayed_innovation_score": 50, "assessment_status": innovation_status, "innovation_data_completeness": 0},
        "srm": {"strategic_index": score, "srm_classification": classification},
        "risk_score": score,
        "quoted_price": 1.0,
        "adjusted_tco": 1.1,
    }


def test_unsupported_innovation_and_esg_awards_are_withheld():
    results = generate_supplier_recommendations([_profile("A", 80), _profile("B", 60)])
    by_role = {item["Recommendation"]: item for item in results}
    assert by_role["Most Innovative Supplier"]["Supplier"] == "No Qualified Supplier"
    assert by_role["Most Sustainable Supplier"]["Supplier"] == "No Qualified Supplier"


def test_long_term_requires_financial_esg_and_innovation_evidence():
    results = generate_supplier_recommendations([_profile("A", 80), _profile("B", 60)])
    by_role = {item["Recommendation"]: item for item in results}
    assert by_role["Best Long-Term Supplier"]["Supplier"] == "No Qualified Supplier"


def test_every_recommendation_has_governance_fields():
    results = generate_supplier_recommendations([_profile("A", 80), _profile("B", 60)])
    assert all(item["Evidence Status"] and item["Human Review Status"] and item["Governance"] for item in results)
