from pathlib import Path

import pytest

import modules.flexible_laminate_cost as laminate_cost_module
from modules.category_cost_router import calculate_category_should_cost
from modules.commodity_library import get_commodity_profile
from modules.data_loader import get_demo_data, get_flexible_laminate_demo_suppliers
from modules.flexible_laminate_cost import (
    SUPPORTED_STRUCTURES,
    calculate_flexible_laminate_should_cost,
    compounded_yield,
    tooling_amortisation_per_kg,
)
from modules.flexible_laminate_validation import validate_flexible_laminate_dataframe
from modules.validation import validate_rfq_dataframe


def _base_assumptions(category="Packaging Procurement", commodity=None):
    values = {
        "category": category,
        "annual_volume": 500000,
        "demand_change": 0,
        "fx_rate": 83,
        "raw_material_shock": 0,
        "freight_shock": 0,
    }
    if commodity is not None:
        values["commodity"] = commodity
    return values


def test_flexible_laminates_registered_under_packaging_only():
    profile = get_commodity_profile("Packaging Procurement", "Flexible Laminates")
    assert profile["unit"] == "kg"
    assert profile["structures"] == ["PET / PE", "PET / MetPET / PE", "BOPP / CPP"]
    assert get_commodity_profile("Raw Material Procurement", "Flexible Laminates") == {}


@pytest.mark.parametrize("structure", list(SUPPORTED_STRUCTURES))
def test_all_three_structures_reconcile_cost_and_mass(structure):
    result = calculate_flexible_laminate_should_cost(structure=structure)
    material_shares = {key: value for key, value in SUPPORTED_STRUCTURES[structure].items() if key != "layer_count"}
    assert sum(material_shares.values()) == pytest.approx(1.0)
    assert result["material_mass_share_total"] == pytest.approx(1.0)
    assert result["target_unit_cost_usd"] == pytest.approx(sum(result["components"].values()))
    assert result["unit"] == "kg"


def test_total_micron_is_explicit_metadata_only():
    low = calculate_flexible_laminate_should_cost(total_micron=35)
    high = calculate_flexible_laminate_should_cost(total_micron=140)
    assert low["target_unit_cost_usd"] == pytest.approx(high["target_unit_cost_usd"])
    assert "metadata only" in low["total_micron_basis"].lower()


def test_compounded_loss_is_not_simple_addition():
    yield_factor = compounded_yield(3, 2, 1)
    assert yield_factor == pytest.approx(0.97 * 0.98 * 0.99)
    assert (1 - yield_factor) * 100 < 6


def test_new_tooling_amortisation():
    value = tooling_amortisation_per_kg(
        "Up to 4 colours", "Rotogravure", 4, 250, 250000, "New", "Not applicable"
    )
    assert value == pytest.approx(0.004)


def test_existing_tooling_requires_yes_evidence():
    with pytest.raises(ValueError, match="availability confirmation"):
        tooling_amortisation_per_kg(
            "Up to 4 colours", "Rotogravure", 4, 250, 250000, "Existing", "Not assessed"
        )
    assert tooling_amortisation_per_kg(
        "Up to 4 colours", "Rotogravure", 4, 250, 250000, "Existing", "Yes"
    ) == 0


@pytest.mark.parametrize("availability", ["Yes", "No", "Not assessed"])
def test_new_tooling_rejects_existing_tooling_evidence(availability):
    with pytest.raises(ValueError, match="New tooling"):
        tooling_amortisation_per_kg(
            "Up to 4 colours", "Rotogravure", 4, 250, 250000, "New", availability
        )


def test_unprinted_tooling_contract_is_fully_normalized():
    assert tooling_amortisation_per_kg(
        "Unprinted", "Rotogravure", 0, 0, 250000, "Not applicable", "Not applicable"
    ) == 0
    with pytest.raises(ValueError, match="Unprinted"):
        tooling_amortisation_per_kg(
            "Unprinted", "Rotogravure", 0, 0, 250000, "Not applicable", "Yes"
        )


@pytest.mark.parametrize(
    "profile,colours",
    [("Unprinted", 1), ("Up to 4 colours", 5), ("5–8 colours", 4)],
)
def test_print_profile_colour_mismatch_fails(profile, colours):
    with pytest.raises(ValueError, match="inconsistent"):
        calculate_flexible_laminate_should_cost(print_profile=profile, number_of_colours=colours)


def test_fractional_colour_count_fails_before_conversion():
    assumptions = _base_assumptions(commodity="Flexible Laminates")
    assumptions["laminate_number_of_colours"] = 4.8
    with pytest.raises(ValueError, match="whole number"):
        calculate_category_should_cost(assumptions)


def test_category_router_uses_laminate_engine():
    assumptions = _base_assumptions(commodity="Flexible Laminates")
    assumptions.update({
        "laminate_structure": "PET / MetPET / PE",
        "laminate_total_micron": 85,
        "laminate_print_profile": "Up to 4 colours",
        "laminate_print_process": "Rotogravure",
        "laminate_number_of_colours": 4,
        "laminate_adhesive_type": "Solvent-free",
        "laminate_printing_loss_pct": 3,
        "laminate_lamination_loss_pct": 2,
        "laminate_slitting_loss_pct": 1,
        "laminate_tooling_status": "New",
        "laminate_existing_tooling_available": "Not applicable",
        "laminate_tooling_cost_per_colour_usd": 250,
        "laminate_tooling_lifetime_volume_kg": 250000,
    })
    result, frame = calculate_category_should_cost(assumptions)
    assert result["commodity"] == "Flexible Laminates"
    assert result["structure"] == "PET / MetPET / PE"
    assert "Unit Cost USD/kg" in frame.columns


def test_raw_material_default_restored_to_pet_resin():
    result, _ = calculate_category_should_cost(_base_assumptions("Raw Material Procurement"))
    assert result["commodity"] == "PET Resin"


def test_packaging_default_remains_corrugated():
    default_result, _ = calculate_category_should_cost(_base_assumptions("Packaging Procurement"))
    explicit_result, _ = calculate_category_should_cost(_base_assumptions("Packaging Procurement", "Corrugated Board"))
    assert default_result["target_unit_cost_usd"] == pytest.approx(explicit_result["target_unit_cost_usd"])


@pytest.mark.parametrize("structure", list(SUPPORTED_STRUCTURES))
def test_each_selected_structure_returns_three_comparable_suppliers(structure):
    data = get_flexible_laminate_demo_suppliers(structure)
    assert len(data) == 3
    assert set(data["Laminate Structure"]) == {structure}
    assert set(data["Unit"]) == {"kg"}
    assert set(data["Material"]) == {"Flexible Laminates"}
    assert validate_flexible_laminate_dataframe(data, structure)["is_valid"]


def test_structure_calls_are_state_isolated():
    bopp = get_flexible_laminate_demo_suppliers("BOPP / CPP")
    pet = get_flexible_laminate_demo_suppliers("PET / PE")
    bopp_again = get_flexible_laminate_demo_suppliers("BOPP / CPP")
    assert set(bopp["Laminate Structure"]) == {"BOPP / CPP"}
    assert set(pet["Laminate Structure"]) == {"PET / PE"}
    assert set(bopp_again["Laminate Structure"]) == {"BOPP / CPP"}


def test_no_global_structure_setter_or_getter_remains():
    assert not hasattr(laminate_cost_module, "_SELECTED_STRUCTURE")
    assert not hasattr(laminate_cost_module, "set_selected_laminate_structure")
    assert not hasattr(laminate_cost_module, "get_selected_laminate_structure")


def test_get_demo_data_requires_and_uses_explicit_c2_structure():
    with pytest.raises(ValueError, match="explicit selected_structure"):
        get_demo_data("Packaging Procurement", "Flexible Laminates")
    data = get_demo_data(
        "Packaging Procurement",
        "Flexible Laminates",
        selected_structure="BOPP / CPP",
    )
    assert data.attrs["assumption_profile_version"] == "C2.0"
    assert data.attrs["selected_laminate_structure"] == "BOPP / CPP"
    assert set(data["Laminate Structure"]) == {"BOPP / CPP"}


def test_valid_demo_passes_dedicated_and_shared_validation():
    data = get_demo_data(
        "Packaging Procurement",
        "Flexible Laminates",
        selected_structure="PET / PE",
    )
    assert validate_flexible_laminate_dataframe(data, "PET / PE")["is_valid"]
    assert validate_rfq_dataframe(
        data,
        "Packaging Procurement",
        "Flexible Laminates",
        selected_structure="PET / PE",
    )["is_valid"]


def test_validation_depends_only_on_explicit_structure():
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    assert validate_flexible_laminate_dataframe(data, "PET / PE")["is_valid"]
    mismatch = validate_flexible_laminate_dataframe(data, "BOPP / CPP")
    assert not mismatch["is_valid"]
    assert any("selected laminate structure" in item for item in mismatch["errors"])


def test_validation_without_explicit_structure_fails_closed():
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    result = validate_flexible_laminate_dataframe(data, None)
    assert not result["is_valid"]
    assert any("explicit selected structure" in item for item in result["errors"])


def test_synthetic_and_uploaded_paths_share_explicit_validation_contract():
    synthetic = get_demo_data(
        "Packaging Procurement",
        "Flexible Laminates",
        selected_structure="PET / MetPET / PE",
    )
    uploaded_like = synthetic.copy(deep=True)
    uploaded_like.attrs.clear()
    assert validate_rfq_dataframe(
        synthetic,
        "Packaging Procurement",
        "Flexible Laminates",
        selected_structure="PET / MetPET / PE",
    )["is_valid"]
    assert validate_rfq_dataframe(
        uploaded_like,
        "Packaging Procurement",
        "Flexible Laminates",
        selected_structure="PET / MetPET / PE",
    )["is_valid"]


def test_app_passes_explicit_structure_to_loading_and_validation():
    source = Path("app.py").read_text(encoding="utf-8")
    assert "selected_structure=selected_laminate_structure" in source
    assert source.count("selected_structure=selected_laminate_structure") >= 3


def test_mixed_supported_structures_fail():
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    data.loc[0, "Laminate Structure"] = "BOPP / CPP"
    result = validate_flexible_laminate_dataframe(data, "PET / PE")
    assert not result["is_valid"]
    assert any("selected laminate structure" in item for item in result["errors"])


def test_invalid_structure_fails():
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    data.loc[0, "Laminate Structure"] = "PET / Foil / PE"
    result = validate_flexible_laminate_dataframe(data, "PET / PE")
    assert not result["is_valid"]
    assert any("Unsupported" in item for item in result["errors"])


def test_fractional_layer_count_fails_without_dtype_warning():
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    data["Layer Count"] = data["Layer Count"].astype(float)
    data.loc[0, "Layer Count"] = 2.5
    result = validate_flexible_laminate_dataframe(data, "PET / PE")
    assert not result["is_valid"]
    assert any("whole number" in item for item in result["errors"])


def test_mixed_materials_fail():
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    data.loc[0, "Material"] = "Kraft Paper"
    assert not validate_flexible_laminate_dataframe(data, "PET / PE")["is_valid"]


def test_mixed_units_fail():
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    data.loc[0, "Unit"] = "piece"
    assert not validate_flexible_laminate_dataframe(data, "PET / PE")["is_valid"]


def test_micron_bounds_fail():
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    data.loc[0, "Total Micron"] = 20
    assert not validate_flexible_laminate_dataframe(data, "PET / PE")["is_valid"]


def test_print_tooling_consistency_fails():
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    data.loc[0, "Print Profile"] = "Unprinted"
    assert not validate_flexible_laminate_dataframe(data, "PET / PE")["is_valid"]


def test_existing_tooling_without_availability_fails_validation():
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    data.loc[0, "Tooling Status"] = "Existing"
    data.loc[0, "Existing Tooling Available"] = "Not assessed"
    assert not validate_flexible_laminate_dataframe(data, "PET / PE")["is_valid"]


def test_new_tooling_with_existing_availability_fails_validation():
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    data.loc[0, "Existing Tooling Available"] = "Yes"
    assert not validate_flexible_laminate_dataframe(data, "PET / PE")["is_valid"]


def test_loss_bounds_fail():
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    data.loc[0, "Printing Loss %"] = 9
    assert not validate_flexible_laminate_dataframe(data, "PET / PE")["is_valid"]


def test_corrugated_non_regression():
    data = get_demo_data("Packaging Procurement", "Corrugated Board")
    assert set(data["Unit"]) == {"piece"}


def test_kraft_non_regression():
    data = get_demo_data("Raw Material Procurement", "Kraft Paper")
    assert set(data["Material"]) == {"Kraft Paper"}
    assert set(data["Unit"]) == {"kg"}


def test_pet_resin_non_regression():
    data = get_demo_data("Raw Material Procurement", "PET Resin")
    assert set(data["Material"]) == {"PET Resin"}
    assert set(data["Unit"]) == {"kg"}
