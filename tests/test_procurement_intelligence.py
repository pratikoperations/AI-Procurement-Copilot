"""Regression tests for Build 0.9.3 procurement intelligence."""

from modules.allocation_optimizer import optimize_allocation
from modules.data_loader import get_demo_suppliers
from modules.decision_engine import generate_decision
from modules.negotiation_engine import build_negotiation_intelligence
from modules.risk_intelligence import assess_procurement_risks
from modules.scenario_engine import run_intelligence_scenario
from modules.scoring import enrich_supplier_scores
from modules.strategy_engine import recommend_strategy


ASSUMPTIONS = {
    "annual_volume": 500000,
    "raw_material_shock": 0.0,
    "freight_shock": 0.0,
    "demand_change": 0.0,
}


def _scored():
    return enrich_supplier_scores(get_demo_suppliers(), ASSUMPTIONS)


def test_decision_engine_is_deterministic():
    scored = _scored()
    allocation = optimize_allocation(scored, ASSUMPTIONS["annual_volume"])
    first = generate_decision(scored, allocation["allocation_df"])
    second = generate_decision(scored, allocation["allocation_df"])
    assert first == second
    assert first["recommended_supplier"] == scored.iloc[0]["Supplier"]
    assert 0 <= first["award_confidence"] <= 100
    assert "not black-box AI" in first["explainability"]["governance"]


def test_strategy_engine_returns_supported_strategy():
    result = recommend_strategy(_scored(), ASSUMPTIONS["annual_volume"])
    assert result["strategy"] in {
        "Single Source", "Dual Source", "Multi Source", "Strategic Partnership",
        "Competitive Tender", "Long-Term Agreement", "Spot Buy",
    }
    assert result["reason"]


def test_allocation_optimizer_totals_one_hundred():
    result = optimize_allocation(_scored(), ASSUMPTIONS["annual_volume"])
    allocation = result["allocation_df"]
    assert round(allocation["Recommended Allocation %"].sum(), 6) == 100
    assert len(allocation) <= 2
    assert result["explanation"]


def test_negotiation_intelligence_has_one_row_per_supplier():
    scored = _scored()
    result = build_negotiation_intelligence(scored, ASSUMPTIONS["annual_volume"], 0.35)
    assert len(result) == len(scored)
    assert (result["Target Price USD"] <= scored["Quoted Unit Price USD"].max()).all()
    assert set(result["Negotiation Priority"]).issubset({"High", "Medium", "Low"})


def test_risk_intelligence_returns_ranked_risks():
    scored = _scored()
    allocation = optimize_allocation(scored, ASSUMPTIONS["annual_volume"])
    result = assess_procurement_risks(scored, allocation["allocation_df"])
    assert len(result["risks"]) >= 8
    assert result["highest_severity"] in {"Critical", "High", "Medium", "Low"}
    assert result["top_mitigation"]


def test_scenario_engine_recomputes_recommendation():
    result = run_intelligence_scenario(get_demo_suppliers(), ASSUMPTIONS, "Price Increase")
    assert result["scenario"] == "Price Increase"
    assert not result["scored_df"].empty
    assert result["decision"]["recommended_supplier"]
    assert round(result["allocation"]["allocation_df"]["Recommended Allocation %"].sum(), 6) == 100
