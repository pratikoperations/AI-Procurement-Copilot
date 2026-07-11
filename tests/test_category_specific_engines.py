"""Regression tests for Build 0.9.4 category-specific cost and risk engines."""

from modules.category_cost_router import calculate_category_should_cost
from modules.category_engine import get_category_profile, is_production_ready
from modules.data_loader import get_demo_data
from modules.raw_material_cost import calculate_raw_material_should_cost
from modules.raw_material_risk import calculate_raw_material_risk
from modules.raw_material_tco import calculate_raw_material_tco
from modules.scoring import enrich_supplier_scores

RAW_ASSUMPTIONS = {
    "category": "Raw Material Procurement",
    "commodity": "PET Resin",
    "annual_volume": 500000,
    "raw_material_shock": 0.0,
    "freight_shock": 0.0,
    "demand_change": 0.0,
    "fx_rate": 83,
}


def test_raw_material_engine_is_active():
    profile = get_category_profile("Raw Material Procurement", "PET Resin")
    assert profile["engine_status"] == "Active"
    assert is_production_ready("Raw Material Procurement") is True


def test_raw_material_should_cost_responds_to_commodity_shock():
    base = calculate_raw_material_should_cost("PET Resin")
    shocked = calculate_raw_material_should_cost("PET Resin", commodity_shock=0.20)
    assert shocked["target_unit_cost_usd"] > base["target_unit_cost_usd"]


def test_raw_material_risk_penalizes_high_dependency_supplier():
    low = {"Commodity Volatility %":10,"Import Dependency %":20,"Supplier Concentration %":30,"Substitute Available":"Yes","Capacity Buffer %":25,"Quality PPM":400,"Currency":"INR","Lead Time Days":15,"Payment Terms":"Net 60","Incoterms":"DDP"}
    high = {"Commodity Volatility %":35,"Import Dependency %":90,"Supplier Concentration %":85,"Substitute Available":"No","Capacity Buffer %":3,"Quality PPM":2500,"Currency":"USD","Lead Time Days":70,"Payment Terms":"Advance 50%","Incoterms":"EXW"}
    assert calculate_raw_material_risk(low)["risk_score"] > calculate_raw_material_risk(high)["risk_score"]


def test_raw_material_tco_contains_category_specific_costs():
    supplier = get_demo_data("Raw Material Procurement", "PET Resin").iloc[0].to_dict()
    result = calculate_raw_material_tco(supplier, 500000)
    assert result["adjusted_tco_unit_usd"] > supplier["Quoted Unit Price USD"]
    assert "duty_cost_usd" in result
    assert "volatility_buffer_usd" in result


def test_category_scoring_routes_to_raw_material_engine():
    scored = enrich_supplier_scores(get_demo_data("Raw Material Procurement", "PET Resin"), RAW_ASSUMPTIONS)
    assert not scored.empty
    assert set(scored["category_engine"]) == {"Raw Material Procurement"}
    assert scored["total_score"].between(0, 100).all()


def test_category_cost_router_uses_raw_material_model():
    result, frame = calculate_category_should_cost(RAW_ASSUMPTIONS)
    assert result["commodity"] == "PET Resin"
    assert "Commodity Index" in frame["Component"].tolist()
