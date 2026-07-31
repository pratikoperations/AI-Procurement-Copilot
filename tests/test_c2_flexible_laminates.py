import math

import pandas as pd
import pytest

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


def test_flexible_laminates_registered_under_packaging_only():
    profile = get_commodity_profile("Packaging Procurement", "Flexible Laminates")
    assert profile["unit"] == "kg"
    assert profile["structures"] == ["PET / PE", "PET / MetPET / PE", "BOPP / CPP"]
    assert get_commodity_profile("Raw Material Procurement", "Flexible Laminates") == {}


@pytest.mark.parametrize("structure", list(SUPPORTED_STRUCTURES))
def test_all_three_structures_reconcile(structure):
    result = calculate_flexible_laminate_should_cost(structure=structure)
    assert result["unit"] == "kg"
    assert result["target_unit_cost_usd"] == pytest.approx(sum(result["components"].values()))
    assert result["target_unit_cost_usd"] > 0


def test_compounded_loss_is_not_simple_addition():
    yield_factor = compounded_yield(3, 2, 1)
    assert yield_factor == pytest.approx(0.97 * 0.98 * 0.99)
    assert (1 - yield_factor) * 100 < 6


def test_tooling_amortisation():
    value = tooling_amortisation_per_kg("Up to 4 colours", "Rotogravure", 4, 250, 250000, "New")
    assert value == pytest.approx(0.004)


def test_unprinted_tooling_inconsistency_fails():
    with pytest.raises(ValueError, match="Unprinted"):
        tooling_amortisation_per_kg("Unprinted", "Rotogravure", 1, 250, 250000, "New")


def test_category_router_uses_laminate_engine():
    result, frame = calculate_category_should_cost({
        "category": "Packaging Procurement",
        "commodity": "Flexible Laminates",
        "annual_volume": 500000,
        "demand_change": 0,
        "fx_rate": 83,
        "raw_material_shock": 0,
        "freight_shock": 0,
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
        "laminate_tooling_cost_per_colour_usd": 250,
        "laminate_tooling_lifetime_volume_kg": 250000,
    })
    assert result["commodity"] == "Flexible Laminates"
    assert result["structure"] == "PET / MetPET / PE"
    assert "Unit Cost USD/kg" in frame.columns


def test_controlled_demo_dataset():
    data = get_flexible_laminate_demo_suppliers()
    assert len(data) == 3
    assert set(data["Laminate Structure"]) == set(SUPPORTED_STRUCTURES)
    assert set(data["Unit"]) == {"kg"}
    assert set(data["Material"]) == {"Flexible Laminates"}


def test_get_demo_data_routes_c2():
    data = get_demo_data("Packaging Procurement", "Flexible Laminates")
    assert data.attrs["assumption_profile_version"] == "C2.0"
    assert list(data["Supplier"]) == ["Precision Flexibles Ltd", "BarrierPack Films", "Circular Laminate Solutions"]


def test_valid_demo_passes_dedicated_and_shared_validation():
    data = get_demo_data("Packaging Procurement", "Flexible Laminates")
    assert validate_flexible_laminate_dataframe(data)["is_valid"]
    assert validate_rfq_dataframe(data, "Packaging Procurement", "Flexible Laminates")["is_valid"]


def test_invalid_structure_fails():
    data = get_flexible_laminate_demo_suppliers()
    data.loc[0, "Laminate Structure"] = "PET / Foil / PE"
    result = validate_flexible_laminate_dataframe(data)
    assert not result["is_valid"]
    assert any("Unsupported" in item for item in result["errors"])


def test_mixed_materials_fail():
    data = get_flexible_laminate_demo_suppliers()
    data.loc[0, "Material"] = "Kraft Paper"
    assert not validate_flexible_laminate_dataframe(data)["is_valid"]


def test_mixed_units_fail():
    data = get_flexible_laminate_demo_suppliers()
    data.loc[0, "Unit"] = "piece"
    assert not validate_flexible_laminate_dataframe(data)["is_valid"]


def test_micron_bounds_fail():
    data = get_flexible_laminate_demo_suppliers()
    data.loc[0, "Total Micron"] = 20
    assert not validate_flexible_laminate_dataframe(data)["is_valid"]


def test_print_tooling_consistency_fails():
    data = get_flexible_laminate_demo_suppliers()
    data.loc[0, "Print Profile"] = "Unprinted"
    assert not validate_flexible_laminate_dataframe(data)["is_valid"]


def test_loss_bounds_fail():
    data = get_flexible_laminate_demo_suppliers()
    data.loc[0, "Printing Loss %"] = 9
    assert not validate_flexible_laminate_dataframe(data)["is_valid"]


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
