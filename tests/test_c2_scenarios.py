import pytest

from modules.data_loader import get_demo_data, get_flexible_laminate_demo_suppliers
from modules.scenario import run_scenario_table
from modules.scenario_engine import (
    FLEXIBLE_LAMINATE_SCENARIOS,
    apply_flexible_laminate_scenario,
    run_all_flexible_laminate_scenarios,
    run_flexible_laminate_scenario,
)


def _assumptions(structure="PET / PE"):
    return {
        "category": "Packaging Procurement",
        "commodity": "Flexible Laminates",
        "laminate_structure": structure,
        "annual_volume": 500000,
        "raw_material_shock": 0.0,
        "freight_shock": 0.0,
        "demand_change": 0.0,
        "fx_rate": 83.0,
        "category_profile": {"unit": "kg"},
    }


def test_exact_governed_scenario_set():
    assert FLEXIBLE_LAMINATE_SCENARIOS == (
        "Base Case",
        "Polymer Index +20%",
        "MetPET Availability Stress",
        "Adhesive and Conversion Cost +15%",
        "Demand +25%",
        "Press and Lamination Capacity Stress",
        "Tooling Replacement Scenario",
    )


def test_all_seven_scenarios_run_in_deterministic_order():
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    results = run_all_flexible_laminate_scenarios(data, _assumptions())
    assert [result["scenario"] for result in results] == list(FLEXIBLE_LAMINATE_SCENARIOS)
    assert len(results) == 7


def test_base_case_does_not_mutate_source_data():
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    original = data.copy(deep=True)
    scenario_df, scenario_assumptions, metadata = apply_flexible_laminate_scenario(
        data, _assumptions(), "Base Case"
    )
    assert scenario_df.equals(original)
    assert data.equals(original)
    assert scenario_assumptions["demand_change"] == 0.0
    assert metadata["applicable"]


def test_polymer_index_stresses_price_only_not_capability_or_tooling():
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    stressed, _, metadata = apply_flexible_laminate_scenario(
        data, _assumptions(), "Polymer Index +20%"
    )
    assert (stressed["Quoted Unit Price USD"] > data["Quoted Unit Price USD"]).all()
    for column in [
        "Printing Capability Score",
        "Lamination Capability Score",
        "Application Approval Status",
        "Tooling Status",
        "Tooling Availability",
    ]:
        assert stressed[column].equals(data[column])
    assert metadata["polymer_index_change"] == pytest.approx(0.20)


def test_adhesive_conversion_stress_is_isolated_from_polymer_and_capability():
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    stressed, _, metadata = apply_flexible_laminate_scenario(
        data, _assumptions(), "Adhesive and Conversion Cost +15%"
    )
    assert (stressed["Quoted Unit Price USD"] > data["Quoted Unit Price USD"]).all()
    assert metadata["adhesive_conversion_change"] == pytest.approx(0.15)
    assert "polymer_index_change" not in metadata
    assert stressed["Substrate Availability %"].equals(data["Substrate Availability %"])
    assert stressed["Printing Capability Score"].equals(data["Printing Capability Score"])


def test_metpet_stress_applies_only_to_three_layer_structure():
    metpet = get_flexible_laminate_demo_suppliers("PET / MetPET / PE")
    stressed, _, metadata = apply_flexible_laminate_scenario(
        metpet, _assumptions("PET / MetPET / PE"), "MetPET Availability Stress"
    )
    assert metadata["applicable"]
    assert (stressed["Quoted Unit Price USD"] > metpet["Quoted Unit Price USD"]).all()
    assert (stressed["Substrate Availability %"] < metpet["Substrate Availability %"]).all()

    pet_pe = get_flexible_laminate_demo_suppliers("PET / PE")
    unchanged, _, metadata = apply_flexible_laminate_scenario(
        pet_pe, _assumptions("PET / PE"), "MetPET Availability Stress"
    )
    assert not metadata["applicable"]
    assert unchanged.equals(pet_pe)


def test_demand_scenario_reconciles_effective_volume_and_annual_tco():
    result = run_flexible_laminate_scenario(
        get_flexible_laminate_demo_suppliers("PET / PE"),
        _assumptions(),
        "Demand +25%",
    )
    assert result["effective_annual_volume"] == pytest.approx(625000)
    assert (result["scored_df"]["effective_annual_volume"] == 625000).all()
    for _, row in result["scored_df"].iterrows():
        assert row["annual_tco_usd"] == pytest.approx(
            row["adjusted_tco_unit_usd"] * 625000,
            abs=1.0,
        )


def test_capacity_stress_recalculates_eligibility_and_no_winner():
    result = run_flexible_laminate_scenario(
        get_flexible_laminate_demo_suppliers("PET / PE"),
        _assumptions(),
        "Press and Lamination Capacity Stress",
    )
    assert not result["scored_df"]["technical_eligible"].any()
    assert result["winner"] is None
    assert result["decision"]["recommended_supplier"] == "No technically eligible supplier"
    assert result["standard_allocation_df"].empty
    assert result["optimized_allocation"]["allocation_df"].empty


def test_tooling_replacement_adds_amortisation_without_false_unavailability():
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    data["Tooling Status"] = "Existing"
    data["Existing Tooling Available"] = "Yes"
    data["Tooling Availability"] = "Yes"
    stressed, _, metadata = apply_flexible_laminate_scenario(
        data, _assumptions(), "Tooling Replacement Scenario"
    )
    expected = (
        data["Number of Colours"].astype(float)
        * data["Tooling Cost per Colour USD"].astype(float)
        / data["Tooling Lifetime Volume kg"].astype(float)
    )
    assert stressed["Quoted Unit Price USD"].tolist() == pytest.approx(
        (data["Quoted Unit Price USD"] + expected).tolist()
    )
    assert set(stressed["Tooling Status"]) == {"New"}
    assert set(stressed["Tooling Availability"]) == {"Not applicable"}
    assert metadata["tooling_amortisation_added"]


def test_every_applicable_scenario_winner_is_eligible():
    results = run_all_flexible_laminate_scenarios(
        get_flexible_laminate_demo_suppliers("PET / PE"), _assumptions()
    )
    for result in results:
        if result["winner"] is not None:
            assert bool(result["winner"]["technical_eligible"])


def test_scenario_table_never_falls_back_to_ineligible_supplier():
    table = run_scenario_table(
        get_flexible_laminate_demo_suppliers("PET / PE"), _assumptions()
    )
    capacity = table.loc[
        table["Scenario"] == "Press and Lamination Capacity Stress"
    ].iloc[0]
    assert capacity["Winning Supplier"] == "No technically eligible supplier"
    assert capacity["Standard Allocation Status"] == "No allocation"
    assert capacity["Optimized Allocation Status"] == "No allocation"


def test_generic_and_laminate_penalties_reconcile_in_every_scenario():
    for result in run_all_flexible_laminate_scenarios(
        get_flexible_laminate_demo_suppliers("PET / PE"), _assumptions()
    ):
        for _, row in result["scored_df"].iterrows():
            assert row["combined_risk_penalty_usd"] == pytest.approx(
                row["generic_risk_penalty_usd"] + row["laminate_risk_penalty_usd"],
                abs=1e-4,
            )
            assert row["adjusted_tco_unit_usd"] == pytest.approx(
                row["base_adjusted_tco_unit_usd"] + row["laminate_risk_penalty_usd"],
                abs=1e-4,
            )


def test_structure_context_fails_closed_on_mismatch():
    data = get_flexible_laminate_demo_suppliers("BOPP / CPP")
    with pytest.raises(ValueError, match="must match"):
        apply_flexible_laminate_scenario(
            data, _assumptions("PET / PE"), "Base Case"
        )


def test_scenario_non_regression_existing_categories():
    corrugated = get_demo_data("Packaging Procurement", "Corrugated Board")
    kraft = get_demo_data("Raw Material Procurement", "Kraft Paper")
    pet = get_demo_data("Raw Material Procurement", "PET Resin")
    assert set(corrugated["Unit"]) == {"piece"}
    assert set(kraft["Material"]) == {"Kraft Paper"}
    assert set(pet["Material"]) == {"PET Resin"}
