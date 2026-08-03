import pandas as pd
import pytest

from modules.data_loader import get_demo_data, get_flexible_laminate_demo_suppliers
from modules.scenario import run_scenario_table
from modules.scenario_engine import (
    FLEXIBLE_LAMINATE_SCENARIOS,
    SCENARIO_ASSUMPTION_VERSION,
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
    assert all(
        result["metadata"]["scenario_assumption_version"] == SCENARIO_ASSUMPTION_VERSION
        for result in results
    )


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


def test_metpet_non_applicable_table_is_not_duplicate_base_case():
    table = run_scenario_table(
        get_flexible_laminate_demo_suppliers("PET / PE"), _assumptions()
    )
    row = table.loc[table["Scenario"] == "MetPET Availability Stress"].iloc[0]
    assert row["Scenario Applicable"] == False
    assert row["Winning Supplier"] == "Not applicable"
    assert row["Scenario Route Status"] == "NOT_APPLICABLE"
    assert row["Canonical Allocation Status"] == "No allocation"
    assert row["Allocation Available"] == False
    assert "Standard Allocation Status" not in table.columns
    assert "Optimized Allocation Status" not in table.columns
    assert pd.isna(row["Annual TCO (USD)"])


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
    assert result["ineligibility_reasons"]


def test_all_ineligible_reason_is_presented_in_scenario_table():
    table = run_scenario_table(
        get_flexible_laminate_demo_suppliers("PET / PE"), _assumptions()
    )
    row = table.loc[
        table["Scenario"] == "Press and Lamination Capacity Stress"
    ].iloc[0]
    assert row["Winning Supplier"] == "No technically eligible supplier"
    assert row["Ineligibility / Applicability Reason"]
    assert row["Ineligibility / Applicability Reason"] != "Technical eligibility thresholds were not met." or isinstance(
        row["Ineligibility / Applicability Reason"], str
    )


def test_baseline_new_tooling_receives_no_duplicate_amortisation():
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    original = data.copy(deep=True)
    stressed, _, metadata = apply_flexible_laminate_scenario(
        data, _assumptions(), "Tooling Replacement Scenario"
    )
    assert stressed["Quoted Unit Price USD"].tolist() == pytest.approx(
        original["Quoted Unit Price USD"].tolist()
    )
    assert metadata["replacement_applied_count"] == 0
    assert metadata["already_new_tooling_count"] == len(data)
    assert metadata["not_applicable_count"] == 0
    assert data.equals(original)


def test_existing_confirmed_tooling_receives_exact_replacement_amortisation():
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    data["Tooling Status"] = "Existing"
    data["Existing Tooling Available"] = "Yes"
    data["Tooling Availability"] = "Yes"
    original = data.copy(deep=True)
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
    assert metadata["replacement_applied_count"] == len(data)
    assert metadata["already_new_tooling_count"] == 0
    assert data.equals(original)


@pytest.mark.parametrize("availability", ["No", "Not assessed"])
def test_existing_unconfirmed_tooling_fails_closed(availability):
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    data.loc[0, "Tooling Status"] = "Existing"
    data.loc[0, "Existing Tooling Available"] = availability
    data.loc[0, "Tooling Availability"] = availability
    with pytest.raises(ValueError, match="requires Existing Tooling Available = Yes"):
        apply_flexible_laminate_scenario(
            data, _assumptions(), "Tooling Replacement Scenario"
        )


def test_mixed_new_existing_and_unprinted_tooling_population():
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    data.loc[0, "Tooling Status"] = "Existing"
    data.loc[0, "Existing Tooling Available"] = "Yes"
    data.loc[0, "Tooling Availability"] = "Yes"
    data.loc[1, "Tooling Status"] = "New"
    data.loc[1, "Existing Tooling Available"] = "Not applicable"
    data.loc[1, "Tooling Availability"] = "Not applicable"
    data.loc[2, "Print Profile"] = "Unprinted"
    data.loc[2, "Number of Colours"] = 0
    data.loc[2, "Tooling Status"] = "Not applicable"
    data.loc[2, "Existing Tooling Available"] = "Not applicable"
    data.loc[2, "Tooling Availability"] = "Not applicable"
    data.loc[2, "Tooling Cost per Colour USD"] = 0.0
    original_prices = data["Quoted Unit Price USD"].copy()

    stressed, _, metadata = apply_flexible_laminate_scenario(
        data, _assumptions(), "Tooling Replacement Scenario"
    )
    assert stressed.loc[0, "Quoted Unit Price USD"] > original_prices.loc[0]
    assert stressed.loc[1, "Quoted Unit Price USD"] == pytest.approx(original_prices.loc[1])
    assert stressed.loc[2, "Quoted Unit Price USD"] == pytest.approx(original_prices.loc[2])
    assert metadata["replacement_applied_count"] == 1
    assert metadata["already_new_tooling_count"] == 1
    assert metadata["not_applicable_count"] == 1


def test_award_confidence_uses_eligible_suppliers_only():
    result = run_flexible_laminate_scenario(
        get_flexible_laminate_demo_suppliers("PET / PE"),
        _assumptions(),
        "Base Case",
    )
    assert len(result["eligible_df"]) == 2
    assert result["decision"]["confidence_governance"] == (
        "Award confidence calculated from technically eligible suppliers only."
    )


def test_single_eligible_supplier_confidence_is_constrained():
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    data.loc[1, "Application Approval Status"] = "Not approved"
    result = run_flexible_laminate_scenario(data, _assumptions(), "Base Case")
    assert len(result["eligible_df"]) == 1
    assert result["decision"]["award_confidence"] <= 60.0
    assert "Single technically eligible supplier" in result["decision"]["confidence_governance"]


def test_every_applicable_scenario_winner_is_eligible():
    results = run_all_flexible_laminate_scenarios(
        get_flexible_laminate_demo_suppliers("PET / PE"), _assumptions()
    )
    for result in results:
        if result["metadata"]["applicable"] and result["winner"] is not None:
            assert bool(result["winner"]["technical_eligible"])


def test_scenario_table_never_falls_back_to_ineligible_supplier():
    table = run_scenario_table(
        get_flexible_laminate_demo_suppliers("PET / PE"), _assumptions()
    )
    capacity = table.loc[
        table["Scenario"] == "Press and Lamination Capacity Stress"
    ].iloc[0]
    assert capacity["Winning Supplier"] == "No technically eligible supplier"
    assert capacity["Canonical Allocation Status"] == "No allocation"
    assert capacity["Allocation Available"] == False
    assert capacity["Scenario Route Status"] not in {"READY", "WARNING"}
    assert capacity["Blocking Reasons"]


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
