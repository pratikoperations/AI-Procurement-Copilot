import math

import pytest

from modules.assumption_provenance import build_assumption_register, provenance_counts
from modules.calculation_catalogue import ASSUMPTIONS, CALCULATIONS, HUMAN_REVIEW_BOUNDARY
from modules.calculation_explorer_adapter import authoritative_value, build_explorer_payload
from modules.calculation_reconciliation import assert_reconciled
from modules.flexible_laminate_cost import calculate_flexible_laminate_should_cost
from modules.raw_material_cost import calculate_raw_material_should_cost
from modules.steel_cost import add_steel_currency_values, calculate_steel_should_cost


def test_catalogue_ids_are_unique_and_metadata_complete():
    calculation_ids = [item.calculation_id for item in CALCULATIONS]
    assumption_ids = [item.assumption_id for item in ASSUMPTIONS]
    assert len(calculation_ids) == len(set(calculation_ids))
    assert len(assumption_ids) == len(set(assumption_ids))
    for item in CALCULATIONS:
        assert item.business_name
        assert item.formula_text
        assert item.unit
        assert item.source_module
        assert item.downstream_outputs
        assert item.governance_caveat
    for item in ASSUMPTIONS:
        assert item.business_name
        assert item.key
        assert item.unit
        assert item.source_module
        assert item.edit_scope in {"none", "controlled", "scenario"}
        assert isinstance(item.editable, bool)
        assert item.validation_rules
        assert item.governance_caveat


def test_provenance_is_deterministic_and_preserves_values():
    assumptions = {"annual_volume": 500000, "fx_rate": 83, "derived_test": 42}
    register = build_assumption_register(
        assumptions,
        supplied_keys={"annual_volume"},
        inferred_keys={"fx_rate"},
        derived_keys={"derived_test"},
    )
    by_key = {item["key"]: item for item in register}
    assert by_key["annual_volume"]["status"] == "supplied"
    assert by_key["fx_rate"]["status"] == "inferred"
    assert by_key["derived_test"]["status"] == "derived"
    assert by_key["derived_test"]["value"] == 42
    assert provenance_counts(register) == {
        "defaulted": 0,
        "derived": 1,
        "inferred": 1,
        "supplied": 1,
    }


def test_kraft_authoritative_components_reconcile():
    result = calculate_raw_material_should_cost(
        "Kraft Paper",
        kraft_variant="Recycled Kraft",
        gsm=150,
        strength_grade="22 BF",
    )
    component_result = {
        "components": {
            key: result[key]
            for key in (
                "commodity_index",
                "conversion_premium",
                "freight",
                "duty",
                "quality_premium",
                "supplier_margin",
            )
        },
        "target_unit_cost_usd": result["target_unit_cost_usd"],
    }
    payload = build_explorer_payload(
        context={"category": "Raw Material Procurement", "commodity": "Kraft Paper"},
        assumptions={"annual_volume": 500000, "fx_rate": 83},
        authoritative_results={"KRF-001": result["target_unit_cost_usd"]},
        reconciliation_inputs={"component_results": {"kraft": component_result}},
    )
    assert payload["reconciliation"]["components:kraft"]["passed"]
    assert authoritative_value(payload, "KRF-001") == result["target_unit_cost_usd"]


def test_flexible_laminate_authoritative_components_reconcile():
    result = calculate_flexible_laminate_should_cost()
    payload = build_explorer_payload(
        context={"category": "Packaging Procurement", "commodity": "Flexible Laminates"},
        assumptions={"annual_volume": 500000, "fx_rate": 83},
        authoritative_results={"LAM-004": result["target_unit_cost_usd"]},
        reconciliation_inputs={"component_results": {"laminate": result}},
    )
    assert payload["reconciliation"]["components:laminate"]["passed"]
    assert authoritative_value(payload, "LAM-004") == result["target_unit_cost_usd"]


def test_steel_components_annual_and_currency_reconcile():
    result = calculate_steel_should_cost(
        "PPGI_COIL_Z120",
        500000,
        base_steel_usd_per_kg=0.72,
        profile_premium_usd_per_kg=0.05,
        rolling_conversion_usd_per_kg=0.10,
        zinc_cost_usd_per_kg=0.08,
        paint_treatment_usd_per_kg=0.12,
        energy_surcharge_usd_per_kg=0.04,
        yield_pct=96.0,
        slitting_cutting_usd_per_kg=0.025,
        packing_usd_per_kg=0.015,
        freight_usd_per_kg=0.045,
        sourcing_route="Import",
        import_duty_pct=10.0,
        supplier_margin_pct=8.0,
    )
    enriched = add_steel_currency_values(result, 83, "Both")
    payload = build_explorer_payload(
        context={"category": "Raw Material Procurement", "commodity": "Steel"},
        assumptions={"annual_volume": 500000, "fx_rate": 83, "steel_profile": "PPGI_COIL_Z120"},
        authoritative_results={"STL-003": result["target_unit_cost_usd"]},
        reconciliation_inputs={
            "component_results": {"steel": result},
            "annual_values": {
                "steel": {
                    "unit_value": result["target_unit_cost_usd"],
                    "annual_volume": result["annual_volume_kg"],
                    "annual_value": result["annual_value_usd"],
                }
            },
            "currency_values": {
                "steel_unit": {
                    "usd_value": enriched["unit_cost_usd_per_kg"],
                    "fx_rate": enriched["usd_inr_fx_rate"],
                    "inr_value": enriched["unit_cost_inr_per_kg"],
                }
            },
        },
    )
    assert assert_reconciled(payload["reconciliation"])
    assert authoritative_value(payload, "STL-003") == result["target_unit_cost_usd"]


def test_formula_metadata_is_not_executable_and_result_is_unchanged():
    sentinel = {"authoritative": 123.456}
    payload = build_explorer_payload(
        context={},
        assumptions={},
        authoritative_results={"COM-001": sentinel},
    )
    calculation = payload["calculations"][0]
    assert calculation["formula_executable"] is False
    assert authoritative_value(payload, "COM-001") is sentinel
    assert "eval" not in calculation["formula_text"].lower()


def test_human_review_boundary_is_mandatory():
    payload = build_explorer_payload(context={}, assumptions={}, authoritative_results={})
    assert payload["human_review"]["required"] is True
    assert payload["human_review"]["boundary"] == HUMAN_REVIEW_BOUNDARY
    assert "No autonomous award" in HUMAN_REVIEW_BOUNDARY


def test_steel_catalogue_uses_dedicated_scenario_sources():
    steel_scenario = next(item for item in CALCULATIONS if item.calculation_id == "SCN-003")
    generic_scenario = next(item for item in CALCULATIONS if item.calculation_id == "SCN-001")
    assert "steel" in steel_scenario.source_module.lower()
    assert steel_scenario.source_module != generic_scenario.source_module
    assert "scenario_engine.py" not in steel_scenario.source_module
