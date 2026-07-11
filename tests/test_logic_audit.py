"""Build 0.9.6 formula and safety invariants."""

from modules.category_cost_router import calculate_category_should_cost
from modules.data_loader import get_demo_data
from modules.scoring import enrich_supplier_scores
from modules.validation_assurance import safe_executive_text


def _assumptions(category, commodity):
    return {
        "category": category,
        "commodity": commodity,
        "annual_volume": 500000,
        "raw_material_shock": 0.0,
        "freight_shock": 0.0,
        "demand_change": 0.0,
        "fx_rate": 83,
    }


def test_packaging_and_raw_material_costs_are_positive_and_category_specific():
    packaging = _assumptions("Packaging Procurement", "Corrugated Board")
    raw = _assumptions("Raw Material Procurement", "PET Resin")
    pack_cost, _ = calculate_category_should_cost(packaging)
    raw_cost, _ = calculate_category_should_cost(raw)
    assert pack_cost["target_unit_cost_usd"] > 0
    assert raw_cost["target_unit_cost_usd"] > 0
    assert raw_cost.get("commodity") == "PET Resin"
    assert pack_cost != raw_cost


def test_all_scoring_outputs_remain_in_range():
    for category, commodity in [("Packaging Procurement", "Corrugated Board"), ("Raw Material Procurement", "PET Resin")]:
        assumptions = _assumptions(category, commodity)
        scored = enrich_supplier_scores(get_demo_data(category, commodity), assumptions)
        for column in ["risk_score", "performance_score", "esg_score", "total_score"]:
            assert scored[column].between(0, 100).all()
        assert (scored["adjusted_tco_unit_usd"] > 0).all()
        assert (scored["annual_tco_usd"] > 0).all()


def test_blocked_status_withholds_award_language():
    eligibility = {
        "status":"Blocked",
        "reason":"Invalid critical data",
        "failed_checks":["Negative price"],
        "required_remediation":["Correct input"],
        "final_award_language_allowed":False,
    }
    text = safe_executive_text(eligibility, "Award Supplier A")
    assert "WITHHELD" in text
    assert "Award Supplier A" not in text
