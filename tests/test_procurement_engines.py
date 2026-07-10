"""Core regression tests for AI Procurement Copilot."""

from modules.data_loader import get_demo_suppliers
from modules.scoring import enrich_supplier_scores
from modules.should_cost import calculate_packaging_should_cost
from modules.validation import validate_rfq_dataframe, validate_scored_output


BASE_ASSUMPTIONS = {
    "annual_volume": 500000,
    "raw_material_shock": 0.0,
    "freight_shock": 0.0,
    "demand_change": 0.0,
}


def test_demo_rfq_is_valid():
    df = get_demo_suppliers()
    result = validate_rfq_dataframe(df)
    assert result["is_valid"] is True
    assert result["errors"] == []


def test_should_cost_is_positive_and_component_linked():
    result = calculate_packaging_should_cost()
    component_total = sum(
        value for key, value in result.items() if key != "target_unit_cost_usd"
    )
    assert result["target_unit_cost_usd"] > 0
    assert round(result["target_unit_cost_usd"], 6) == round(component_total, 6)


def test_raw_material_shock_increases_should_cost():
    base = calculate_packaging_should_cost()
    stressed = calculate_packaging_should_cost(raw_material_shock=0.20)
    assert stressed["target_unit_cost_usd"] > base["target_unit_cost_usd"]


def test_supplier_scoring_outputs_are_valid():
    df = get_demo_suppliers()
    scored = enrich_supplier_scores(df, BASE_ASSUMPTIONS)
    result = validate_scored_output(scored)
    assert result["is_valid"] is True
    assert len(scored) == len(df)


def test_supplier_scores_are_sorted_descending():
    df = get_demo_suppliers()
    scored = enrich_supplier_scores(df, BASE_ASSUMPTIONS)
    scores = scored["total_score"].tolist()
    assert scores == sorted(scores, reverse=True)


def test_annual_tco_matches_unit_tco_times_effective_volume():
    df = get_demo_suppliers()
    scored = enrich_supplier_scores(df, BASE_ASSUMPTIONS)
    for _, row in scored.iterrows():
        expected = row["adjusted_tco_unit_usd"] * BASE_ASSUMPTIONS["annual_volume"]
        assert abs(row["annual_tco_usd"] - expected) < 100
