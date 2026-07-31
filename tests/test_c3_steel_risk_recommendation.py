"""Focused governed tests for C3.4 Steel risk, scoring and recommendation."""

import copy

import pandas as pd
import pytest

from modules.data_loader import get_demo_data, get_steel_demo_suppliers
from modules.steel_risk import (
    DEFAULT_STEEL_RISK_ASSUMPTIONS,
    STEEL_RISK_WEIGHTS,
    calculate_generic_supplier_risk,
    calculate_steel_specific_risk,
    score_and_recommend_steel_suppliers,
)


def supplier(name="Bharat Steelworks Ltd"):
    frame = get_steel_demo_suppliers()
    return frame.loc[frame["Supplier"] == name].iloc[0].to_dict()


def decision(mode="USD", suppliers=None, assumptions=None, profile="PPGI_COIL_Z120"):
    return score_and_recommend_steel_suppliers(
        suppliers if suppliers is not None else get_steel_demo_suppliers(),
        profile,
        1_000_000,
        83.0,
        display_mode=mode,
        risk_assumptions=assumptions,
    )


def test_steel_risk_weights_cover_exact_dimensions_and_reconcile():
    expected = {
        "steel_index_volatility", "ore_or_scrap_exposure", "energy_exposure", "mill_allocation",
        "import_dependency", "fx_exposure", "duty_exposure", "grade_substitution_dependency",
        "coating_line_dependency", "paint_line_dependency", "source_concentration",
        "capacity_utilisation", "coil_weight_mismatch", "quality_continuity", "delivery_continuity",
    }
    assert set(STEEL_RISK_WEIGHTS) == expected
    assert sum(STEEL_RISK_WEIGHTS.values()) == pytest.approx(1.0)


def test_every_steel_risk_dimension_is_returned():
    result = calculate_steel_specific_risk(supplier(), "PPGI_COIL_Z120")
    assert set(result["steel_risk_dimensions"]) == set(STEEL_RISK_WEIGHTS)
    assert 0 <= result["steel_risk_score"] <= 100


@pytest.mark.parametrize("value,expected", [(15, 0), (15.1, 50), (30, 50), (30.1, 100)])
def test_steel_index_threshold_boundaries(value, expected):
    result = calculate_steel_specific_risk(supplier(), "CR_COIL_COMMERCIAL", {"steel_index_volatility_pct": value})
    assert result["steel_risk_dimensions"]["steel_index_volatility"] == expected


@pytest.mark.parametrize("field", [
    "Mill Allocation %", "Import Dependency %", "Supplier Concentration %", "Capacity Utilisation %",
    "Quality Continuity Score", "OTIF %", "Coil Weight Min MT", "Coil Weight Max MT",
])
def test_missing_steel_risk_evidence_fails_closed(field):
    row = supplier()
    row.pop(field)
    with pytest.raises(ValueError, match="Missing Steel risk evidence"):
        calculate_steel_specific_risk(row, "CR_COIL_COMMERCIAL")


def test_contradictory_coil_weight_evidence_fails_closed():
    row = supplier()
    row["Coil Weight Min MT"] = 20
    row["Coil Weight Max MT"] = 10
    with pytest.raises(ValueError, match="Contradictory coil-weight"):
        calculate_steel_specific_risk(row, "CR_COIL_COMMERCIAL")


def test_profile_dependencies_are_applicable_only():
    assumptions = {"coating_line_dependency_pct": 80, "paint_line_dependency_pct": 80}
    cr = calculate_steel_specific_risk(supplier(), "CR_COIL_COMMERCIAL", assumptions)["steel_risk_dimensions"]
    gi = calculate_steel_specific_risk(supplier(), "GI_COIL_Z120", assumptions)["steel_risk_dimensions"]
    ppgi = calculate_steel_specific_risk(supplier(), "PPGI_COIL_Z120", assumptions)["steel_risk_dimensions"]
    assert cr["coating_line_dependency"] == 0
    assert cr["paint_line_dependency"] == 0
    assert gi["coating_line_dependency"] == 100
    assert gi["paint_line_dependency"] == 0
    assert ppgi["coating_line_dependency"] == 100
    assert ppgi["paint_line_dependency"] == 100


def test_generic_and_steel_risk_remain_separate_outputs():
    scored, _ = decision()
    assert "generic_risk_score" in scored
    assert "steel_risk_score" in scored
    assert "generic_risk_band" in scored
    assert "steel_risk_band" in scored
    assert not scored["generic_risk_score"].equals(scored["steel_risk_score"])


def test_generic_risk_missing_evidence_fails_closed():
    row = supplier()
    row.pop("Audit Score")
    with pytest.raises(ValueError, match="Missing generic risk evidence"):
        calculate_generic_supplier_risk(row)


def test_eligible_only_scoring_excludes_lowest_price_ineligible_supplier():
    scored, recommendation = decision()
    global_row = scored.loc[scored["Supplier"] == "Global Coil Trading"].iloc[0]
    assert global_row["normalized_usd_per_kg"] == pytest.approx(0.99)
    assert global_row["technical_eligible"] is False or not bool(global_row["technical_eligible"])
    assert global_row["governed_total_score"] == 0
    assert recommendation["winner"] != "Global Coil Trading"


def test_normalized_usd_ranking_uses_inr_conversion():
    scored, _ = decision()
    prime = scored.loc[scored["Supplier"] == "PrimeCoated Metals"].iloc[0]
    assert prime["normalized_usd_per_kg"] == pytest.approx(96.30 / 83.0)


def test_deterministic_ranking_and_winner():
    first, first_rec = decision()
    second, second_rec = decision()
    assert first["Supplier"].tolist() == second["Supplier"].tolist()
    assert first["governed_total_score"].tolist() == second["governed_total_score"].tolist()
    assert first_rec == second_rec


def test_recommendation_is_human_governed_not_autonomous_award():
    _, recommendation = decision()
    assert recommendation["winner"] is not None
    assert recommendation["human_approval_required"] is True
    assert recommendation["autonomous_award"] is False
    assert "pending human approval" in recommendation["winner_state"].lower()


def test_no_winner_state_when_all_suppliers_ineligible():
    suppliers = get_steel_demo_suppliers().copy()
    suppliers["Application Approval"] = "Pending"
    scored, recommendation = decision(suppliers=suppliers, profile="CR_COIL_COMMERCIAL")
    assert scored["technical_eligible"].sum() == 0
    assert recommendation["winner"] is None
    assert recommendation["winner_state"] == "No winner — no technically eligible supplier"


def test_risk_cannot_override_technical_ineligibility():
    suppliers = get_steel_demo_suppliers().copy()
    idx = suppliers.index[suppliers["Supplier"] == "Global Coil Trading"][0]
    suppliers.loc[idx, "Risk Category"] = "Low"
    suppliers.loc[idx, "Mill Allocation %"] = 10
    suppliers.loc[idx, "Import Dependency %"] = 0
    suppliers.loc[idx, "Supplier Concentration %"] = 0
    suppliers.loc[idx, "Capacity Utilisation %"] = 10
    suppliers.loc[idx, "Quality Continuity Score"] = 100
    suppliers.loc[idx, "OTIF %"] = 100
    scored, recommendation = decision(suppliers=suppliers)
    row = scored.loc[scored["Supplier"] == "Global Coil Trading"].iloc[0]
    assert not bool(row["technical_eligible"])
    assert row["governed_total_score"] == 0
    assert recommendation["winner"] != "Global Coil Trading"


@pytest.mark.parametrize("mode", ["USD", "INR", "Both"])
def test_display_modes_preserve_winner_and_scores(mode):
    scored, recommendation = decision(mode=mode)
    assert recommendation["winner"] is not None
    assert scored.attrs["display_mode"] == mode


def test_display_mode_full_invariance():
    outputs = [decision(mode) for mode in ("USD", "INR", "Both")]
    winners = [rec["winner"] for _, rec in outputs]
    rankings = [frame["Supplier"].tolist() for frame, _ in outputs]
    scores = [frame["governed_total_score"].tolist() for frame, _ in outputs]
    assert winners[0] == winners[1] == winners[2]
    assert rankings[0] == rankings[1] == rankings[2]
    assert scores[0] == scores[1] == scores[2]


def test_invalid_risk_assumption_fails_closed():
    with pytest.raises(ValueError):
        decision(assumptions={"steel_index_volatility_pct": -1})


def test_default_assumptions_are_explicit_and_complete():
    assert set(DEFAULT_STEEL_RISK_ASSUMPTIONS) == {
        "steel_index_volatility_pct", "ore_or_scrap_exposure_pct", "energy_exposure_pct",
        "fx_exposure_pct", "duty_exposure_pct", "grade_substitution_dependency_pct",
        "coating_line_dependency_pct", "paint_line_dependency_pct",
    }


def test_non_steel_routes_remain_available():
    assert not get_demo_data("Raw Material Procurement", "PET Resin").empty
    assert not get_demo_data("Raw Material Procurement", "Kraft Paper").empty
    assert not get_demo_data("Packaging Procurement", "Corrugated Board").empty
    assert not get_demo_data("Packaging Procurement", "Flexible Laminates", selected_structure="PET / PE").empty
