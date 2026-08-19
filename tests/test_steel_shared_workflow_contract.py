"""End-to-end deterministic assurance for Steel participation in the shared workflow."""

from __future__ import annotations

import json

import pytest

from modules.category_cost_router import calculate_category_should_cost
from modules.currency_unit_governance import normalize_comparison_basis
from modules.data_loader import get_demo_data
from modules.decision_engine import generate_decision, generate_executive_narrative
from modules.executive_outputs import (
    generate_executive_memo,
    generate_explainability_panel,
    generate_supplier_email,
)
from modules.exports import (
    build_decision_package_json,
    build_excel_workbook,
    build_readable_allocation,
    build_readable_supplier_comparison,
    build_readable_supplier_scores,
)
from modules.multi_supplier_allocation_application import (
    route_allows_allocation,
    run_application_allocation,
)
from modules.negotiation import generate_negotiation_playbook, simulate_negotiation
from modules.negotiation_engine import build_negotiation_intelligence
from modules.recommendation import (
    executive_value_breakdown,
    recommendation_confidence,
)
from modules.risk_intelligence import assess_procurement_risks
from modules.scenario import run_scenario_table
from modules.scenario_engine import run_intelligence_scenario
from modules.scoring import enrich_supplier_scores
from modules.strategy_engine import recommend_strategy
from modules.supplier_comparison import build_supplier_intelligence
from modules.validation import validate_rfq_dataframe, validate_scored_output
from modules.validation_assurance import run_validation_assurance


def _assumptions(profile: str) -> dict:
    return {
        "data_source": "Synthetic Demo",
        "category": "Raw Material Procurement",
        "commodity": "Steel",
        "steel_profile": profile,
        "steel_sourcing_route": "Domestic",
        "steel_zinc_cost_usd_per_kg": 0.08 if profile != "CR_COIL_COMMERCIAL" else 0.0,
        "steel_paint_treatment_usd_per_kg": 0.12 if profile == "PPGI_COIL_Z120" else 0.0,
        "steel_import_duty_pct": 0.0,
        "steel_substitution_status": "Non-applicable",
        "annual_volume": 500000.0,
        "annual_volume_unit": "kg",
        "fx_rate": 83.0,
        "display_currency": "Both",
        "raw_material_shock": 0.0,
        "freight_shock": 0.0,
        "demand_change": 0.0,
        "required_awardee_count": 2,
        "minimum_awarded_share_pct": 10.0,
        "max_supplier_share": 75.0,
        "min_backup_share": 15.0,
        "min_risk_score": 0.0,
        "min_esg_score": 50.0,
        "capacity_utilization_ceiling_pct": 90.0,
        "comparison_currency": "USD",
        "required_supplier_ids": (),
        "excluded_supplier_ids": (),
        "procurement_intelligence_scenario": "Base Case",
        "category_profile": {"unit": "kg"},
    }


def _steel_demo(fx_rate: float = 83.0):
    demo = get_demo_data(
        "Raw Material Procurement",
        "Steel",
        expanded_supplier_pool=True,
    )
    return normalize_comparison_basis(demo, fx_rate, "USD")


@pytest.mark.parametrize(
    "profile",
    ["CR_COIL_COMMERCIAL", "GI_COIL_Z120", "PPGI_COIL_Z120"],
)
def test_steel_shared_workflow_reaches_outputs_without_generic_tco_fabrication(profile):
    assumptions = _assumptions(profile)
    suppliers = _steel_demo(assumptions["fx_rate"])

    rfq_validation = validate_rfq_dataframe(
        suppliers,
        category=assumptions["category"],
        commodity=assumptions["commodity"],
    )
    assert rfq_validation["is_valid"], rfq_validation["errors"]

    scored = enrich_supplier_scores(suppliers, assumptions)
    assert validate_scored_output(scored)["is_valid"]
    assert scored.attrs["steel_governed_path"] is True
    assert not scored.empty

    recommended = scored.iloc[0]
    confidence = recommendation_confidence(scored)
    should_cost, should_cost_df = calculate_category_should_cost(assumptions)
    value_metrics = executive_value_breakdown(
        scored,
        assumptions["annual_volume"],
        should_cost["target_unit_cost_usd"],
    )

    application_allocation = run_application_allocation(scored, assumptions)
    allocation_df = application_allocation.allocation_df
    assert route_allows_allocation(application_allocation.route_result)
    assert not allocation_df.empty

    scenario_df = run_scenario_table(suppliers, assumptions)
    assert len(scenario_df) == 7

    negotiation_result = simulate_negotiation(recommended, assumptions["annual_volume"])
    assert negotiation_result["annual_saving_usd"] >= 0
    assert "Governed Steel commercial-price-only simulation" in negotiation_result["simulation_basis"]
    for unsupported in (
        "freight_cost_usd",
        "inventory_cost_usd",
        "working_capital_impact_usd",
        "lead_time_buffer_usd",
        "risk_penalty_usd",
    ):
        assert unsupported not in recommended.index

    playbook = generate_negotiation_playbook(
        recommended,
        should_cost["target_unit_cost_usd"],
        scored.sort_values("Quoted Unit Price USD").iloc[0]["Supplier"],
        scored["Quoted Unit Price USD"].min(),
        negotiation_result["annual_saving_usd"],
        category="Raw Material Procurement",
        commodity="Steel",
        unit="kg",
    )
    assert "Steel" in playbook

    risk_result = assess_procurement_risks(scored, allocation_df)
    strategy_result = recommend_strategy(scored, assumptions["annual_volume"])
    intelligence_decision = generate_decision(scored, allocation_df, risk_result)
    negotiation_intelligence = build_negotiation_intelligence(
        scored,
        assumptions["annual_volume"],
        should_cost["target_unit_cost_usd"],
    )
    intelligence_scenario = run_intelligence_scenario(
        suppliers,
        assumptions,
        assumptions["procurement_intelligence_scenario"],
    )
    assert intelligence_decision["recommended_supplier"]
    assert not negotiation_intelligence.empty
    assert intelligence_scenario["scenario"] == "Base Case"

    supplier_intelligence = build_supplier_intelligence(
        scored,
        assumptions["category"],
        assumptions["commodity"],
    )
    assert supplier_intelligence["profiles"]
    assert not supplier_intelligence["comparison_df"].empty

    assurance = run_validation_assurance(
        suppliers,
        scored,
        allocation_df,
        supplier_intelligence["profiles"],
        assumptions,
        rfq_validation,
    )
    eligibility = assurance["eligibility"]
    data_confidence = assurance["data_confidence"]
    assert eligibility["status"]

    explainability = generate_explainability_panel(recommended)
    assert "Governed Steel" in explainability
    assert "governed" in explainability.lower()

    executive_memo = generate_executive_memo(
        scored,
        allocation_df,
        value_metrics,
        confidence,
        eligibility,
        data_confidence,
    )
    supplier_email = generate_supplier_email(
        recommended,
        should_cost["target_unit_cost_usd"],
        assumptions["annual_volume"],
        assumptions["category"],
        assumptions["commodity"],
        assumptions["annual_volume_unit"],
        eligibility,
    )
    narrative = generate_executive_narrative(
        intelligence_decision,
        strategy_result,
        dict(application_allocation.intelligence_allocation),
        risk_result,
        value_metrics["estimated_ebitda_opportunity_usd"],
    )
    assert executive_memo
    assert supplier_email
    assert narrative

    readable_scores = build_readable_supplier_scores(
        scored,
        data_confidence,
        eligibility,
        supplier_intelligence["comparison_df"],
        display_currency=assumptions["display_currency"],
        fx_rate=assumptions["fx_rate"],
        annual_volume=assumptions["annual_volume"],
        annual_volume_unit=assumptions["annual_volume_unit"],
    )
    readable_comparison = build_readable_supplier_comparison(
        supplier_intelligence["comparison_df"],
        data_confidence,
        eligibility,
        display_currency=assumptions["display_currency"],
        fx_rate=assumptions["fx_rate"],
        annual_volume=assumptions["annual_volume"],
        annual_volume_unit=assumptions["annual_volume_unit"],
    )
    readable_allocation = build_readable_allocation(
        allocation_df,
        assumptions["display_currency"],
        assumptions["fx_rate"],
        assumptions["annual_volume"],
        assumptions["annual_volume_unit"],
    )
    assert not readable_scores.empty
    assert not readable_comparison.empty
    assert not readable_allocation.empty

    workbook = build_excel_workbook(
        scored,
        should_cost_df,
        allocation_df,
        scenario_df,
        readable_scores,
        readable_comparison,
        display_currency=assumptions["display_currency"],
        fx_rate=assumptions["fx_rate"],
        annual_volume=assumptions["annual_volume"],
        annual_volume_unit=assumptions["annual_volume_unit"],
    )
    package = build_decision_package_json(
        recommended,
        value_metrics,
        allocation_df,
        scenario_df,
        negotiation_result,
        eligibility,
    )
    assert len(workbook) > 0
    payload = json.loads(package.decode("utf-8"))
    assert payload["recommended_supplier"]["Supplier"] == recommended["Supplier"]
    assert payload["negotiation"]["simulation_basis"].startswith("Governed Steel")
