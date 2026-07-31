"""Focused governed tests for C3.2 Steel should-cost and currency normalization."""

import math

import pytest

from modules.category_cost_router import calculate_category_should_cost
from modules.steel_cost import (
    add_steel_currency_values,
    calculate_steel_should_cost,
    normalize_steel_supplier_quotation,
    steel_should_cost_dataframe,
)


BASE = {
    "annual_volume_kg": 1_000_000,
    "base_steel_usd_per_kg": 0.72,
    "profile_premium_usd_per_kg": 0.05,
    "rolling_conversion_usd_per_kg": 0.10,
    "zinc_cost_usd_per_kg": 0.0,
    "paint_treatment_usd_per_kg": 0.0,
    "energy_surcharge_usd_per_kg": 0.04,
    "yield_pct": 96.0,
    "slitting_cutting_usd_per_kg": 0.025,
    "packing_usd_per_kg": 0.015,
    "freight_usd_per_kg": 0.045,
    "sourcing_route": "Domestic",
    "import_duty_pct": 0.0,
    "supplier_margin_pct": 8.0,
}


def build(profile="CR_COIL_COMMERCIAL", **overrides):
    values = dict(BASE)
    values.update(overrides)
    return calculate_steel_should_cost(profile, **values)


def test_cr_reconciles_and_has_zero_coatings():
    result = build()
    assert result["components"]["Zinc Coating"] == 0
    assert result["components"]["Paint / Treatment"] == 0
    assert sum(result["components"].values()) == pytest.approx(result["target_unit_cost_usd"])


def test_gi_requires_and_applies_zinc():
    result = build("GI_COIL_Z120", zinc_cost_usd_per_kg=0.08)
    assert result["components"]["Zinc Coating"] == pytest.approx(0.08)
    assert result["components"]["Paint / Treatment"] == 0


def test_ppgi_requires_and_applies_zinc_and_paint():
    result = build("PPGI_COIL_Z120", zinc_cost_usd_per_kg=0.08, paint_treatment_usd_per_kg=0.12)
    assert result["components"]["Zinc Coating"] == pytest.approx(0.08)
    assert result["components"]["Paint / Treatment"] == pytest.approx(0.12)


def test_yield_loss_calculation_applies_to_recurring_block_only():
    result = build(yield_pct=80.0)
    recurring = 0.72 + 0.05 + 0.10 + 0.04
    assert result["components"]["Yield-Loss Effect"] == pytest.approx(recurring / 0.80 - recurring)


def test_import_duty_applies_to_pre_duty_landed_subtotal():
    result = build(sourcing_route="Import", import_duty_pct=10.0)
    recurring_gross = (0.72 + 0.05 + 0.10 + 0.04) / 0.96
    landed = recurring_gross + 0.025 + 0.015 + 0.045
    assert result["components"]["Import Duty"] == pytest.approx(landed * 0.10)


def test_domestic_route_rejects_nonzero_import_duty():
    with pytest.raises(ValueError, match="Domestic sourcing requires"):
        build(import_duty_pct=5.0)


def test_supplier_margin_applies_after_duty():
    result = build(sourcing_route="Import", import_duty_pct=10.0, supplier_margin_pct=12.0)
    pre_margin = result["target_unit_cost_usd"] - result["components"]["Supplier Margin"]
    assert result["components"]["Supplier Margin"] == pytest.approx(pre_margin * 0.12)


def test_annual_value_is_unit_cost_times_volume():
    result = build(annual_volume_kg=250_000)
    assert result["annual_value_usd"] == pytest.approx(result["target_unit_cost_usd"] * 250_000)


def test_usd_quote_normalization():
    quote = normalize_steel_supplier_quotation(1.08, "USD", 1_000_000, 83.0, "Both")
    assert quote["normalized_usd_per_kg"] == pytest.approx(1.08)
    assert quote["equivalent_inr_per_kg"] == pytest.approx(89.64)
    assert quote["annual_value_usd"] == pytest.approx(1_080_000)
    assert quote["annual_value_inr"] == pytest.approx(89_640_000)


def test_inr_quote_normalization():
    quote = normalize_steel_supplier_quotation(96.30, "INR", 1_000_000, 83.0, "Both")
    assert quote["normalized_usd_per_kg"] == pytest.approx(96.30 / 83.0)
    assert quote["equivalent_inr_per_kg"] == pytest.approx(96.30)


@pytest.mark.parametrize("mode", ["USD", "INR", "Both"])
def test_display_modes_are_supported_and_preserve_normalized_usd(mode):
    quote = normalize_steel_supplier_quotation(96.30, "INR", 500_000, 83.0, mode)
    assert quote["display_mode"] == mode
    assert quote["normalized_usd_per_kg"] == pytest.approx(96.30 / 83.0)


def test_display_mode_invariance_for_quotation_ordering_inputs():
    values = [
        normalize_steel_supplier_quotation(1.08, "USD", 1000, 83.0, mode)["normalized_usd_per_kg"]
        for mode in ("USD", "INR", "Both")
    ]
    assert values[0] == pytest.approx(values[1]) == pytest.approx(values[2])


def test_should_cost_currency_enrichment_is_invariant_across_modes():
    result = build()
    enriched = [add_steel_currency_values(result, 83.0, mode) for mode in ("USD", "INR", "Both")]
    assert len({item["target_unit_cost_usd"] for item in enriched}) == 1
    assert len({item["unit_cost_usd_per_kg"] for item in enriched}) == 1
    assert len({item["annual_value_usd"] for item in enriched}) == 1


def test_both_dataframe_uses_separate_numeric_currency_fields():
    result = build()
    frame = steel_should_cost_dataframe(result, 83.0, "Both")
    assert list(frame.columns) == [
        "Cost Component",
        "Unit Cost USD/kg",
        "Annual Cost USD",
        "Unit Cost INR/kg",
        "Annual Cost INR",
    ]
    assert all(frame[column].map(lambda value: isinstance(value, RealNumber)).all() for column in frame.columns[1:])
    assert not frame.astype(str).apply(lambda column: column.str.contains(" / ").any()).any()


RealNumber = (int, float)


def test_usd_dataframe_excludes_inr_fields():
    frame = steel_should_cost_dataframe(build(), 83.0, "USD")
    assert "Unit Cost USD/kg" in frame
    assert "Annual Cost USD" in frame
    assert "Unit Cost INR/kg" not in frame
    assert "Annual Cost INR" not in frame


def test_inr_dataframe_excludes_usd_fields():
    frame = steel_should_cost_dataframe(build(), 83.0, "INR")
    assert "Unit Cost INR/kg" in frame
    assert "Annual Cost INR" in frame
    assert "Unit Cost USD/kg" not in frame
    assert "Annual Cost USD" not in frame


@pytest.mark.parametrize("fx", [None, "83", 0, -83, float("nan"), float("inf")])
def test_invalid_fx_fails_closed(fx):
    with pytest.raises(ValueError, match="USD/INR FX rate"):
        normalize_steel_supplier_quotation(1.08, "USD", 1000, fx)


def test_unsupported_quotation_currency_fails_closed():
    with pytest.raises(ValueError, match="Unsupported Steel quotation currency"):
        normalize_steel_supplier_quotation(1.08, "EUR", 1000, 83.0)


@pytest.mark.parametrize(
    "profile, zinc, paint",
    [
        ("CR_COIL_COMMERCIAL", 0.01, 0.0),
        ("CR_COIL_COMMERCIAL", 0.0, 0.01),
        ("GI_COIL_Z120", 0.0, 0.0),
        ("GI_COIL_Z120", 0.08, 0.01),
        ("PPGI_COIL_Z120", 0.0, 0.12),
        ("PPGI_COIL_Z120", 0.08, 0.0),
    ],
)
def test_profile_applicability_failures(profile, zinc, paint):
    with pytest.raises(ValueError):
        build(profile, zinc_cost_usd_per_kg=zinc, paint_treatment_usd_per_kg=paint)


def test_unsupported_profile_fails_closed():
    with pytest.raises(ValueError, match="Unsupported Steel profile"):
        build("UNKNOWN")


@pytest.mark.parametrize(
    "field, value",
    [
        ("base_steel_usd_per_kg", None),
        ("profile_premium_usd_per_kg", "0.05"),
        ("rolling_conversion_usd_per_kg", -0.01),
        ("annual_volume_kg", 0),
        ("yield_pct", 0),
        ("yield_pct", 101),
        ("supplier_margin_pct", -1),
        ("supplier_margin_pct", 100),
    ],
)
def test_invalid_cost_inputs_fail_closed(field, value):
    with pytest.raises(ValueError):
        build(**{field: value})


def test_router_uses_dedicated_steel_engine():
    result, frame = calculate_category_should_cost(
        {
            "category": "Raw Material Procurement",
            "commodity": "Steel",
            "annual_volume": 1_000_000,
            "fx_rate": 83.0,
            "steel_profile": "GI_COIL_Z120",
            "steel_display_mode": "Both",
        }
    )
    assert result["commodity"] == "Steel"
    assert result["profile_id"] == "GI_COIL_Z120"
    assert result["components"]["Zinc Coating"] > 0
    assert "Unit Cost USD/kg" in frame
    assert "Unit Cost INR/kg" in frame


def test_c1_kraft_router_is_preserved():
    result, _ = calculate_category_should_cost(
        {
            "category": "Raw Material Procurement",
            "commodity": "Kraft Paper",
            "annual_volume": 100_000,
            "fx_rate": 83.0,
            "kraft_variant": "Recycled Kraft",
            "kraft_gsm": 150,
            "kraft_strength_grade": "22 BF",
        }
    )
    assert result["commodity"] == "Kraft Paper"


def test_c2_flexible_laminate_router_is_preserved():
    result, _ = calculate_category_should_cost(
        {
            "category": "Packaging Procurement",
            "commodity": "Flexible Laminates",
            "annual_volume": 100_000,
            "fx_rate": 83.0,
        }
    )
    assert result["commodity"] == "Flexible Laminates"
