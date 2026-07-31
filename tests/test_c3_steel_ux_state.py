from pathlib import Path

import pandas as pd
import pytest

from modules.currency_unit_governance import normalize_comparison_basis
from modules.data_loader import get_demo_data, get_steel_demo_suppliers
from modules.scoring import enrich_supplier_scores
from modules.steel_ux import (
    DISPLAY_MODES,
    STEEL_PROFILES,
    apply_steel_state_transition,
    normalize_steel_dependent_state,
)


def base_state(**overrides):
    values = {
        "steel_profile": "CR_COIL_COMMERCIAL",
        "steel_zinc_cost_usd_per_kg": 0.0,
        "steel_paint_treatment_usd_per_kg": 0.0,
        "steel_sourcing_route": "Domestic",
        "steel_import_duty_pct": 0.0,
        "steel_substitution_status": "Non-applicable",
        "steel_scenario": "Base Case",
        "display_currency": "Both",
    }
    values.update(overrides)
    return values


def assumptions(display="Both", profile="CR_COIL_COMMERCIAL"):
    return {
        "category": "Raw Material Procurement",
        "commodity": "Steel",
        "annual_volume": 1_000_000,
        "fx_rate": 83,
        "display_currency": display,
        "steel_profile": profile,
        "steel_substitution_status": "Not applicable",
        "raw_material_shock": 0.0,
        "freight_shock": 0.0,
        "demand_change": 0.0,
    }


@pytest.mark.parametrize("profile", STEEL_PROFILES)
def test_all_three_profiles_are_supported(profile):
    state = normalize_steel_dependent_state(base_state(steel_profile=profile))
    assert state["steel_profile"] == profile


def test_cr_clears_stale_zinc_and_paint():
    state = normalize_steel_dependent_state(base_state(
        steel_profile="CR_COIL_COMMERCIAL",
        steel_zinc_cost_usd_per_kg=0.08,
        steel_paint_treatment_usd_per_kg=0.12,
    ))
    assert state["steel_zinc_cost_usd_per_kg"] == 0.0
    assert state["steel_paint_treatment_usd_per_kg"] == 0.0


def test_gi_requires_zinc_and_clears_stale_paint():
    state = normalize_steel_dependent_state(base_state(
        steel_profile="GI_COIL_Z120",
        steel_zinc_cost_usd_per_kg=0.0,
        steel_paint_treatment_usd_per_kg=0.12,
    ))
    assert state["steel_zinc_cost_usd_per_kg"] == 0.08
    assert state["steel_paint_treatment_usd_per_kg"] == 0.0


def test_ppgi_requires_zinc_and_paint():
    state = normalize_steel_dependent_state(base_state(
        steel_profile="PPGI_COIL_Z120",
        steel_zinc_cost_usd_per_kg=0.0,
        steel_paint_treatment_usd_per_kg=0.0,
    ))
    assert state["steel_zinc_cost_usd_per_kg"] == 0.08
    assert state["steel_paint_treatment_usd_per_kg"] == 0.12


def test_domestic_clears_stale_duty_and_import_restores_controlled_default():
    domestic = normalize_steel_dependent_state(base_state(
        steel_sourcing_route="Domestic", steel_import_duty_pct=18.0
    ))
    assert domestic["steel_import_duty_pct"] == 0.0
    imported = normalize_steel_dependent_state({**domestic, "steel_sourcing_route": "Import"})
    assert imported["steel_import_duty_pct"] == 10.0


@pytest.mark.parametrize(
    "start_profile,end_profile,expected_zinc,expected_paint",
    [
        ("CR_COIL_COMMERCIAL", "GI_COIL_Z120", 0.08, 0.0),
        ("GI_COIL_Z120", "PPGI_COIL_Z120", 0.08, 0.12),
        ("PPGI_COIL_Z120", "CR_COIL_COMMERCIAL", 0.0, 0.0),
    ],
)
def test_bidirectional_profile_transitions_clear_or_restore_dependencies(
    start_profile, end_profile, expected_zinc, expected_paint
):
    session = base_state(
        steel_profile=start_profile,
        steel_zinc_cost_usd_per_kg=0.08,
        steel_paint_treatment_usd_per_kg=0.12,
    )
    state = apply_steel_state_transition(session, end_profile, "Domestic")
    assert state["steel_zinc_cost_usd_per_kg"] == expected_zinc
    assert state["steel_paint_treatment_usd_per_kg"] == expected_paint


def test_bidirectional_domestic_import_transition_clears_stale_duty():
    session = base_state(steel_sourcing_route="Import", steel_import_duty_pct=15.0)
    domestic = apply_steel_state_transition(session, "CR_COIL_COMMERCIAL", "Domestic")
    assert domestic["steel_import_duty_pct"] == 0.0
    imported = apply_steel_state_transition(session, "CR_COIL_COMMERCIAL", "Import")
    assert imported["steel_import_duty_pct"] == 10.0


@pytest.mark.parametrize("display", DISPLAY_MODES)
def test_display_modes_validate_without_changing_governed_state(display):
    state = normalize_steel_dependent_state(base_state(display_currency=display))
    assert state["display_currency"] == display
    assert state["steel_profile"] == "CR_COIL_COMMERCIAL"


def test_inr_quotation_normalizes_before_governed_scoring():
    suppliers = normalize_comparison_basis(get_steel_demo_suppliers(), 83, "USD")
    prime = suppliers.loc[suppliers["Supplier"] == "PrimeCoated Metals"].iloc[0]
    assert prime["Quoted Unit Price USD"] == pytest.approx(96.30 / 83)
    scored = enrich_supplier_scores(suppliers, assumptions())
    assert "steel_risk_score" in scored.columns
    assert "generic_risk_score" in scored.columns
    assert scored.attrs["steel_governed_path"] is True


def test_display_mode_does_not_change_eligibility_ranking_or_winner():
    outputs = []
    for display in DISPLAY_MODES:
        suppliers = normalize_comparison_basis(get_steel_demo_suppliers(), 83, "USD")
        scored = enrich_supplier_scores(suppliers, assumptions(display=display))
        outputs.append((
            scored["technical_eligible"].tolist(),
            scored["Supplier"].tolist(),
            scored.attrs["steel_recommendation"]["winner"],
        ))
    assert outputs[0] == outputs[1] == outputs[2]


def test_no_winner_state_remains_explicit():
    suppliers = normalize_comparison_basis(get_steel_demo_suppliers(), 83, "USD")
    suppliers["Application Approval"] = "Rejected"
    scored = enrich_supplier_scores(suppliers, assumptions())
    assert scored.attrs["steel_recommendation"]["winner"] is None
    assert "No winner" in scored.attrs["steel_recommendation"]["winner_state"]


def test_steel_dashboard_source_surfaces_required_governance_outputs():
    source = Path("modules/steel_ux.py").read_text(encoding="utf-8")
    for phrase in (
        "Generic Supplier Risk",
        "Steel-Specific Risk",
        "Standard Allocation",
        "Optimized Allocation",
        "Unallocated Volume",
        "Human Approval",
        "No autonomous award",
        "engineering approval",
        "live market-data claim",
    ):
        assert phrase.casefold() in source.casefold()
    assert 'width="stretch"' in source
    assert "st.columns(4)" in source


def test_dashboard_routes_steel_to_dedicated_governed_renderer():
    source = Path("modules/dashboard.py").read_text(encoding="utf-8")
    assert "render_steel_governed_dashboard" in source
    assert "is_steel_context" in source


def test_c1_c2_and_generic_demo_routes_remain_available():
    assert not get_demo_data("Raw Material Procurement", "PET Resin").empty
    assert not get_demo_data("Raw Material Procurement", "Kraft Paper").empty
    assert not get_demo_data("Packaging Procurement", "Corrugated Board").empty
    assert not get_demo_data(
        "Packaging Procurement", "Flexible Laminates", selected_structure="PET / PE"
    ).empty
