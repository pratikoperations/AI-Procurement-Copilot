"""Focused governed tests for C3.3 Steel technical eligibility."""

import copy

import pandas as pd
import pytest

from modules.data_loader import get_demo_data, get_steel_demo_suppliers
from modules.steel_validation import (
    evaluate_steel_supplier_eligibility,
    evaluate_steel_supplier_table,
    lowest_price_eligible_supplier,
    steel_eligibility_summary,
)


def supplier(name="Bharat Steelworks Ltd"):
    frame = get_steel_demo_suppliers()
    return frame.loc[frame["Supplier"] == name].iloc[0].to_dict()


def evaluate(row=None, profile="CR_COIL_COMMERCIAL", **kwargs):
    return evaluate_steel_supplier_eligibility(
        row or supplier(),
        profile,
        kwargs.pop("annual_volume_kg", 1_000_000),
        **kwargs,
    )


@pytest.mark.parametrize("profile", ["CR_COIL_COMMERCIAL", "GI_COIL_Z120", "PPGI_COIL_Z120"])
def test_controlled_profiles_are_eligible_for_capable_supplier(profile):
    result = evaluate(profile=profile)
    assert result["eligible"] is True
    assert result["failure_reasons"] == []


def test_unsupported_profile_fails_closed():
    with pytest.raises(ValueError, match="Unsupported Steel profile"):
        evaluate(profile="UNKNOWN")


def test_selected_profile_must_be_explicitly_supported():
    row = supplier()
    row["Supported Steel Profiles"] = "CR_COIL_COMMERCIAL"
    result = evaluate(row, profile="GI_COIL_Z120")
    assert result["eligible"] is False
    assert "Selected profile is not explicitly supported" in result["failure_reasons"]


def test_controlled_grade_family_must_match_profile():
    row = supplier()
    row["Controlled Grade Families"] = "CR commercial demonstration"
    result = evaluate(row, profile="PPGI_COIL_Z120")
    assert "Controlled grade family is not supported" in result["failure_reasons"]


@pytest.mark.parametrize("field", [
    "Supported Steel Profiles", "Controlled Grade Families", "Thickness Min mm", "Thickness Max mm",
    "Width Min mm", "Width Max mm", "Zinc Capability Max g/m²", "Paint Line Capability",
    "Surface Capability", "Supplier or Mill Approval", "Application Approval",
    "Test Certificate Availability", "Supplier Capacity", "Capacity Utilisation %",
    "Coil Weight Min MT", "Coil Weight Max MT",
])
def test_every_mandatory_field_fails_closed_when_missing(field):
    row = supplier()
    row.pop(field)
    result = evaluate(row)
    assert result["eligible"] is False
    assert f"Missing mandatory field: {field}" in result["failure_reasons"]


def test_thickness_boundary_values_are_inclusive():
    row = supplier()
    row["Thickness Min mm"] = 0.80
    row["Thickness Max mm"] = 0.80
    assert evaluate(row)["eligible"] is True


def test_thickness_outside_range_fails():
    row = supplier()
    row["Thickness Max mm"] = 0.79
    assert "Required thickness is outside supplier capability" in evaluate(row)["failure_reasons"]


def test_contradictory_thickness_range_fails():
    row = supplier()
    row["Thickness Min mm"] = 0.90
    row["Thickness Max mm"] = 0.45
    assert "Contradictory thickness capability range" in evaluate(row)["failure_reasons"]


def test_width_band_must_be_fully_supported_at_boundaries():
    row = supplier()
    row["Width Min mm"] = 1000
    row["Width Max mm"] = 1250
    assert evaluate(row)["eligible"] is True


def test_partial_width_support_fails():
    row = supplier()
    row["Width Min mm"] = 1050
    assert "Required width band is not fully supported" in evaluate(row)["failure_reasons"]


def test_gi_zinc_capability_boundary_is_inclusive():
    row = supplier()
    row["Zinc Capability Max g/m²"] = 120
    assert evaluate(row, profile="GI_COIL_Z120")["eligible"] is True


def test_gi_zinc_capability_below_requirement_fails():
    row = supplier()
    row["Zinc Capability Max g/m²"] = 119.9
    assert "Required zinc coating exceeds supplier capability" in evaluate(row, profile="GI_COIL_Z120")["failure_reasons"]


def test_ppgi_requires_paint_line():
    row = supplier()
    row["Paint Line Capability"] = "No"
    assert "Selected profile requires paint-line capability" in evaluate(row, profile="PPGI_COIL_Z120")["failure_reasons"]


def test_cr_does_not_require_paint_line_but_requires_valid_state():
    row = supplier()
    row["Paint Line Capability"] = "No"
    assert evaluate(row)["eligible"] is True
    row["Paint Line Capability"] = "Unknown"
    assert "Paint-line capability is contradictory or unsupported" in evaluate(row)["failure_reasons"]


def test_surface_requirement_must_match():
    row = supplier()
    row["Surface Capability"] = "Controlled galvanized"
    assert "Required surface capability is not supported" in evaluate(row, profile="PPGI_COIL_Z120")["failure_reasons"]


@pytest.mark.parametrize("field,state", [
    ("Supplier or Mill Approval", "Pending"),
    ("Supplier or Mill Approval", "Not approved"),
    ("Application Approval", "Conditional"),
    ("Application Approval", "Rejected"),
])
def test_approval_states_fail_closed(field, state):
    row = supplier()
    row[field] = state
    result = evaluate(row)
    assert result["eligible"] is False


@pytest.mark.parametrize("state", ["Pending", "Unavailable", "Not available", None])
def test_certificate_unavailable_states_fail_closed(state):
    row = supplier()
    row["Test Certificate Availability"] = state
    assert "Test certificate is not available" in evaluate(row)["failure_reasons"]


def test_available_but_not_authenticated_meets_availability_gate_only():
    result = evaluate()
    assert result["eligible"] is True
    assert "technical eligibility only" in result["decision_basis"].lower()


def test_capacity_boundary_is_inclusive():
    row = supplier()
    row["Supplier Capacity"] = 1_000_000
    assert evaluate(row)["eligible"] is True


def test_annual_volume_above_capacity_fails():
    row = supplier()
    row["Supplier Capacity"] = 999_999
    assert "Annual volume exceeds supplier capacity" in evaluate(row)["failure_reasons"]


@pytest.mark.parametrize("utilisation", [-1, 100, 105])
def test_invalid_capacity_utilisation_fails(utilisation):
    row = supplier()
    row["Capacity Utilisation %"] = utilisation
    assert "Capacity utilisation must be within 0% to below 100%" in evaluate(row)["failure_reasons"]


def test_coil_weight_band_must_be_fully_supported():
    row = supplier()
    row["Coil Weight Min MT"] = 5
    row["Coil Weight Max MT"] = 15
    assert evaluate(row)["eligible"] is True
    row["Coil Weight Min MT"] = 6
    assert "Required coil-weight band is not fully supported" in evaluate(row)["failure_reasons"]


@pytest.mark.parametrize("status", ["Pending", "Conditional", "Rejected", "Unavailable", None])
def test_substitution_requested_requires_approved_status(status):
    result = evaluate(substitution_requested=True, substitution_status=status)
    assert "Substitution approval state is not valid for the request" in result["failure_reasons"]


def test_approved_substitution_is_eligible_but_not_engineering_approval():
    result = evaluate(substitution_requested=True, substitution_status="Approved")
    assert result["eligible"] is True
    assert result["decision_basis"] == "Technical eligibility only; price and risk cannot override failures."


def test_exact_profile_accepts_not_applicable_substitution():
    assert evaluate(substitution_requested=False, substitution_status="Not applicable")["eligible"] is True


def test_lowest_price_ineligible_supplier_cannot_win():
    suppliers = get_steel_demo_suppliers().copy()
    suppliers["Normalized USD/kg"] = [1.08, 96.30 / 83.0, 0.99]
    results = evaluate_steel_supplier_table(suppliers, "PPGI_COIL_Z120", 1_000_000)
    assert results.loc[suppliers["Supplier"] == "Global Coil Trading", "eligible"].item() is False
    provisional = lowest_price_eligible_supplier(suppliers, results)
    assert provisional["supplier"] == "Bharat Steelworks Ltd"
    assert provisional["supplier"] != "Global Coil Trading"


def test_risk_category_cannot_override_ineligibility():
    row = supplier("Global Coil Trading")
    row["Risk Category"] = "Low"
    result = evaluate(row, profile="PPGI_COIL_Z120")
    assert result["eligible"] is False


def test_eligible_supplier_count_is_deterministic():
    suppliers = get_steel_demo_suppliers()
    first = evaluate_steel_supplier_table(suppliers, "PPGI_COIL_Z120", 1_000_000)
    second = evaluate_steel_supplier_table(suppliers, "PPGI_COIL_Z120", 1_000_000)
    assert first.attrs["eligible_supplier_count"] == second.attrs["eligible_supplier_count"] == 2


def test_no_eligible_supplier_and_no_winner_states_are_explicit():
    suppliers = get_steel_demo_suppliers().copy()
    suppliers["Application Approval"] = "Pending"
    results = evaluate_steel_supplier_table(suppliers, "CR_COIL_COMMERCIAL", 1_000_000)
    summary = steel_eligibility_summary(results)
    assert summary == {
        "eligible_supplier_count": 0,
        "eligibility_state": "No eligible suppliers",
        "winner_state": "No winner — no technically eligible supplier",
    }
    suppliers["Normalized USD/kg"] = [1.08, 1.16, 0.99]
    assert lowest_price_eligible_supplier(suppliers, results)["supplier"] is None


@pytest.mark.parametrize("mode", ["USD", "INR", "Both"])
def test_display_mode_does_not_change_eligibility(mode):
    result = evaluate(profile="PPGI_COIL_Z120", display_mode=mode)
    assert result["eligible"] is True


def test_display_mode_invariance_across_supplier_table():
    suppliers = get_steel_demo_suppliers()
    states = [
        evaluate_steel_supplier_table(suppliers, "PPGI_COIL_Z120", 1_000_000, display_mode=mode)["eligible"].tolist()
        for mode in ("USD", "INR", "Both")
    ]
    assert states[0] == states[1] == states[2]


def test_unsupported_display_mode_fails_closed():
    with pytest.raises(ValueError, match="Unsupported Steel display mode"):
        evaluate(display_mode="EUR")


@pytest.mark.parametrize("volume", [None, "1000000", 0, -1, float("nan")])
def test_invalid_annual_volume_fails_closed(volume):
    with pytest.raises(ValueError):
        evaluate(annual_volume_kg=volume)


def test_raw_material_steel_route_returns_dedicated_supplier_data():
    frame = get_demo_data("Raw Material Procurement", "Steel")
    assert frame["Supplier"].tolist() == [
        "Bharat Steelworks Ltd", "PrimeCoated Metals", "Global Coil Trading"
    ]


def test_non_steel_routes_remain_available():
    assert not get_demo_data("Raw Material Procurement", "PET Resin").empty
    assert not get_demo_data("Raw Material Procurement", "Kraft Paper").empty
    assert not get_demo_data("Packaging Procurement", "Corrugated Board").empty
    assert not get_demo_data("Packaging Procurement", "Flexible Laminates").empty
