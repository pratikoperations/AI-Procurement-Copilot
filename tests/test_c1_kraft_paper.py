import pandas as pd
import pytest

from modules.allocation import recommend_allocation
from modules.allocation_optimizer import optimize_allocation
from modules.category_cost_router import calculate_category_should_cost
from modules.commodity_library import get_commodities, get_commodity_profile
from modules.data_loader import get_demo_data, get_kraft_paper_demo_suppliers, get_raw_material_demo_suppliers
from modules.kraft_paper_validation import validate_kraft_paper_dataframe
from modules.raw_material_cost import calculate_raw_material_should_cost
from modules.risk_intelligence import assess_procurement_risks
from modules.scenario import run_scenario_table
from modules.scoring import enrich_supplier_scores
from modules.validation import validate_rfq_dataframe


def _assumptions():
    return {
        "category": "Raw Material Procurement",
        "commodity": "Kraft Paper",
        "annual_volume": 100000,
        "raw_material_shock": 0.0,
        "freight_shock": 0.0,
        "demand_change": 0.0,
        "category_profile": {"unit": "kg"},
    }


def test_kraft_paper_registered_under_raw_materials_only():
    assert "Kraft Paper" in get_commodities("Raw Material Procurement")
    assert "Kraft Paper" not in get_commodities("Packaging Procurement")


def test_kraft_profile_is_controlled_and_linked_to_corrugated():
    profile = get_commodity_profile("Raw Material Procurement", "Kraft Paper")
    assert profile["unit"] == "kg"
    assert profile["variants"] == ["Recycled Kraft", "Virgin Kraft"]
    assert profile["downstream_link"] == "Corrugated Board"
    assert profile["source_label"].startswith("Synthetic")


def test_unknown_raw_material_fails_closed():
    with pytest.raises(ValueError, match="Unsupported raw-material commodity"):
        calculate_raw_material_should_cost("Unknown Material")


def test_recycled_kraft_should_cost_has_required_components():
    result = calculate_raw_material_should_cost("Kraft Paper")
    assert result["commodity"] == "Kraft Paper"
    assert result["kraft_variant"] == "Recycled Kraft"
    assert result["gsm"] == 150
    assert result["strength_grade"] == "22 BF"
    assert result["downstream_link"] == "Corrugated Board"
    assert "profile availability" in result["profile_premium_note"].lower()
    assert result["target_unit_cost_usd"] == pytest.approx(sum(result[key] for key in ["commodity_index", "conversion_premium", "freight", "duty", "quality_premium", "supplier_margin"]))


def test_virgin_kraft_costs_more_than_recycled_on_same_profile():
    recycled = calculate_raw_material_should_cost("Kraft Paper", kraft_variant="Recycled Kraft")
    virgin = calculate_raw_material_should_cost("Kraft Paper", kraft_variant="Virgin Kraft")
    assert virgin["target_unit_cost_usd"] > recycled["target_unit_cost_usd"]


def test_higher_strength_and_profile_increase_controlled_premium():
    standard = calculate_raw_material_should_cost("Kraft Paper", gsm=120, strength_grade="18 BF")
    stronger = calculate_raw_material_should_cost("Kraft Paper", gsm=180, strength_grade="28 BF")
    assert stronger["quality_premium"] > standard["quality_premium"]


@pytest.mark.parametrize("kwargs", [
    {"kraft_variant": "Unsupported"},
    {"gsm": 200},
    {"strength_grade": "35 BF"},
])
def test_unsupported_kraft_profiles_fail_closed(kwargs):
    with pytest.raises(ValueError):
        calculate_raw_material_should_cost("Kraft Paper", **kwargs)


@pytest.mark.parametrize("inputs", [
    {"commodity_index": 0.5},
    {"commodity_index": -1, "conversion_premium": 0.1, "freight": 0.1, "duty": 0, "quality_premium": 0.1, "supplier_margin": 0.1},
])
def test_invalid_cost_component_contract_fails_closed(inputs):
    with pytest.raises(ValueError):
        calculate_raw_material_should_cost("Kraft Paper", inputs=inputs)


def test_paper_price_shock_changes_only_expected_cost_basis():
    base = calculate_raw_material_should_cost("Kraft Paper")
    shock = calculate_raw_material_should_cost("Kraft Paper", commodity_shock=0.20)
    assert shock["commodity_index"] == pytest.approx(base["commodity_index"] * 1.20)
    assert shock["freight"] == base["freight"]


def test_kraft_supplier_dataset_has_three_distinct_suppliers():
    df = get_kraft_paper_demo_suppliers()
    assert len(df) == 3
    assert df["Supplier"].nunique() == 3
    assert df["Unit"].eq("kg").all()
    assert df["Material"].eq("Kraft Paper").all()
    assert "Fibre Availability %" in df.columns
    assert "Recycled Fibre Availability %" not in df.columns


def test_demo_router_returns_versioned_synthetic_kraft_data_and_context():
    df = get_demo_data("Raw Material Procurement", "Kraft Paper")
    assert len(df) == 3
    assert df.attrs["source_label"] == "Synthetic demonstration data"
    assert df.attrs["assumption_profile_version"] == "C1.0"
    assert df.attrs["category"] == "Raw Material Procurement"
    assert df.attrs["commodity"] == "Kraft Paper"


def test_unknown_synthetic_raw_material_fails_closed():
    with pytest.raises(ValueError, match="Unsupported synthetic raw-material commodity"):
        get_raw_material_demo_suppliers("Unknown Material")


def test_valid_kraft_supplier_data_passes_with_controlled_warnings():
    result = validate_kraft_paper_dataframe(get_kraft_paper_demo_suppliers())
    assert result["is_valid"]
    assert result["errors"] == []
    assert any("mill allocation" in warning.lower() for warning in result["warnings"])


@pytest.mark.parametrize("column,value,expected", [
    ("Unit", "piece", "kg"),
    ("Kraft Variant", "", "variant"),
    ("GSM", "150 GSM", "non-numeric"),
    ("GSM", 150.5, "whole-number"),
    ("Strength Grade", "", "strength"),
    ("Mill Allocation %", -1, "between 0 and 100"),
    ("Mill Allocation %", 101, "between 0 and 100"),
    ("Fibre Availability %", 101, "between 0 and 100"),
    ("Quality Continuity Score", -1, "between 0 and 100"),
    ("Moisture %", "wet", "non-numeric"),
    ("Corrugated Linkage", "Uncontrolled text", "linkage"),
])
def test_invalid_kraft_fields_fail_with_governed_errors(column, value, expected):
    df = get_kraft_paper_demo_suppliers()
    df.loc[0, column] = value
    result = validate_kraft_paper_dataframe(df)
    assert not result["is_valid"]
    assert any(expected in error.lower() for error in result["errors"])


def test_missing_unit_is_reported_not_raised():
    df = get_kraft_paper_demo_suppliers().drop(columns=["Unit"])
    result = validate_kraft_paper_dataframe(df)
    assert not result["is_valid"]
    assert any("unit" in error.lower() for error in result["errors"])


def test_mixed_material_rows_are_blocked():
    df = get_kraft_paper_demo_suppliers()
    df.loc[2, "Material"] = "Polyethylene"
    result = validate_rfq_dataframe(df, "Raw Material Procurement", "Kraft Paper")
    assert not result["is_valid"]
    assert any("mixed" in error.lower() for error in result["errors"])


def test_selected_commodity_conflict_is_blocked():
    df = get_kraft_paper_demo_suppliers()
    result = validate_rfq_dataframe(df, "Raw Material Procurement", "Polyethylene")
    assert not result["is_valid"]
    assert any("conflicts" in error.lower() for error in result["errors"])


def test_generic_validation_invokes_kraft_controls_from_context():
    df = get_kraft_paper_demo_suppliers()
    df.loc[0, "Moisture %"] = 20
    result = validate_rfq_dataframe(df, "Raw Material Procurement", "Kraft Paper")
    assert not result["is_valid"]
    assert any("moisture" in error.lower() for error in result["errors"])


def test_category_cost_router_passes_kraft_assumptions():
    result, frame = calculate_category_should_cost({
        "category": "Raw Material Procurement", "commodity": "Kraft Paper", "annual_volume": 100000,
        "demand_change": 0.0, "raw_material_shock": 0.0, "freight_shock": 0.0, "fx_rate": 83,
        "kraft_variant": "Virgin Kraft", "kraft_gsm": 180, "kraft_strength_grade": "28 BF",
    })
    assert result["kraft_variant"] == "Virgin Kraft"
    assert result["gsm"] == 180
    assert result["strength_grade"] == "28 BF"
    assert frame["Annual Impact USD"].sum() == pytest.approx(result["target_unit_cost_usd"] * 100000)


def test_kraft_risks_affect_score_and_technical_eligibility():
    df = get_kraft_paper_demo_suppliers()
    scored = enrich_supplier_scores(df, _assumptions())
    circular = scored.loc[scored["Supplier"] == "Circular Paperworks Ltd"].iloc[0]
    western = scored.loc[scored["Supplier"] == "Western Fibre Mills"].iloc[0]
    assert circular["risk_score"] < western["risk_score"]
    assert bool(circular["technical_eligible"])

    df.loc[df["Supplier"] == "Circular Paperworks Ltd", "Mill Allocation %"] = 98
    rescored = enrich_supplier_scores(df, _assumptions())
    circular = rescored.loc[rescored["Supplier"] == "Circular Paperworks Ltd"].iloc[0]
    assert not bool(circular["technical_eligible"])


def test_ineligible_supplier_is_excluded_from_allocations():
    df = get_kraft_paper_demo_suppliers()
    df.loc[df["Supplier"] == "Circular Paperworks Ltd", "Mill Allocation %"] = 98
    scored = enrich_supplier_scores(df, _assumptions())
    allocation = recommend_allocation(scored, 100000)
    optimized = optimize_allocation(scored, 100000)["allocation_df"]
    assert "Circular Paperworks Ltd" not in allocation["Supplier"].tolist()
    assert "Circular Paperworks Ltd" not in optimized["Supplier"].tolist()


def test_executive_risk_output_contains_kraft_specific_risks():
    scored = enrich_supplier_scores(get_kraft_paper_demo_suppliers(), _assumptions())
    result = assess_procurement_risks(scored)
    names = {item["Risk"] for item in result["risks"]}
    assert "Kraft mill allocation risk" in names
    assert "Kraft moisture and yield risk" in names
    assert "Kraft fibre availability risk" in names
    assert "Kraft quality continuity risk" in names


def test_kraft_scenarios_include_price_and_continuity_stress():
    scenarios = run_scenario_table(get_kraft_paper_demo_suppliers(), _assumptions())
    names = scenarios["Scenario"].tolist()
    assert "Paper Price +20%" in names
    assert "Mill / Fibre Continuity Stress" in names
