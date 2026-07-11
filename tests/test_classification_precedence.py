from modules.supplier_recommendation_engine import generate_supplier_recommendations


def _profile(name, score):
    return {
        "supplier_name": name,
        "overall_supplier360_score": score,
        "performance": {"overall_supplier_performance_score": score},
        "financial": {"displayed_financial_score": 80, "assessment_status": "Sufficient Evidence"},
        "esg": {"displayed_esg_score": 75, "assessment_status": "Sufficient Evidence", "esg_data_completeness": 90},
        "innovation": {"displayed_innovation_score": 75, "assessment_status": "Sufficient Evidence", "innovation_data_completeness": 90},
        "srm": {"strategic_index": score, "srm_classification": "Preferred"},
        "risk_score": score,
        "quoted_price": 1.0,
        "adjusted_tco": 1.1,
    }


def test_exit_and_development_candidates_are_different_suppliers():
    results = generate_supplier_recommendations([_profile("A", 85), _profile("B", 60), _profile("C", 30)])
    by_role = {item["Recommendation"]: item["Supplier"] for item in results}
    assert by_role["Exit Candidate"] != by_role["Development Candidate"]


def test_exit_candidate_is_not_long_term_or_strategic_partner():
    results = generate_supplier_recommendations([_profile("A", 85), _profile("B", 60), _profile("C", 30)])
    by_role = {item["Recommendation"]: item["Supplier"] for item in results}
    exit_supplier = by_role["Exit Candidate"]
    assert by_role["Best Long-Term Supplier"] != exit_supplier
    assert by_role["Best Strategic Partner"] != exit_supplier
