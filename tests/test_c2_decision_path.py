import pytest

from modules.allocation import recommend_allocation
from modules.allocation_optimizer import optimize_allocation
from modules.data_loader import get_demo_data, get_flexible_laminate_demo_suppliers
from modules.flexible_laminate_risk import (
    ELIGIBILITY_THRESHOLDS,
    apply_flexible_laminate_risk_to_tco,
    assess_flexible_laminate_supplier,
)
from modules.flexible_laminate_validation import validate_flexible_laminate_dataframe
from modules.risk_intelligence import assess_procurement_risks
from modules.scoring import enrich_supplier_scores
from modules.supplier_comparison import build_supplier_intelligence
from modules.supplier_recommendation_engine import POSITIVE_RECOMMENDATION_ROLES
from modules.validation import validate_rfq_dataframe, validate_scored_output


def _assumptions(structure="PET / PE", demand_change=0.0):
    return {
        "category": "Packaging Procurement",
        "commodity": "Flexible Laminates",
        "laminate_structure": structure,
        "annual_volume": 500000,
        "raw_material_shock": 0,
        "freight_shock": 0,
        "demand_change": demand_change,
        "fx_rate": 83,
    }


def _eligible_record():
    return get_flexible_laminate_demo_suppliers("PET / PE").iloc[0].to_dict()


@pytest.mark.parametrize("field,bounds", ELIGIBILITY_THRESHOLDS.items())
def test_each_eligibility_threshold_boundary_passes(field, bounds):
    minimum, maximum = bounds
    record = _eligible_record()
    record[field] = minimum if minimum is not None else maximum
    assert assess_flexible_laminate_supplier(record)["technical_eligible"]


@pytest.mark.parametrize("field,bounds", ELIGIBILITY_THRESHOLDS.items())
def test_each_eligibility_threshold_breach_fails(field, bounds):
    minimum, maximum = bounds
    record = _eligible_record()
    record[field] = (minimum - 0.1) if minimum is not None else (maximum + 0.1)
    result = assess_flexible_laminate_supplier(record)
    assert not result["technical_eligible"]
    assert any(field in reason for reason in result["technical_ineligibility_reasons"])


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_risk_inputs_fail_closed(value):
    record = _eligible_record()
    record["Substrate Availability %"] = value
    with pytest.raises(ValueError, match="finite"):
        assess_flexible_laminate_supplier(record)


def test_invalid_risk_range_fails_validation():
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    data.loc[0, "Bond Strength Continuity Score"] = 101
    result = validate_flexible_laminate_dataframe(data, "PET / PE")
    assert not result["is_valid"]
    assert any("Bond Strength" in item for item in result["errors"])


def test_application_approval_controls_eligibility():
    record = _eligible_record()
    record["Application Approval Status"] = "Conditional"
    assert not assess_flexible_laminate_supplier(record)["technical_eligible"]


def test_existing_tooling_controls_eligibility():
    record = _eligible_record()
    record["Tooling Status"] = "Existing"
    record["Tooling Availability"] = "Not assessed"
    assert not assess_flexible_laminate_supplier(record)["technical_eligible"]


def test_process_loss_affects_risk_and_tco_without_separate_double_count():
    low = _eligible_record()
    high = dict(low)
    low.update({"adjusted_tco_unit_usd": 2.0, "scenario_unit_price_usd": 1.8, "risk_penalty_usd": 0.03, "failure_probability": 0.08, "Printing Loss %": 1.0, "Lamination Loss %": 1.0, "Slitting Loss %": 0.5})
    high.update({"adjusted_tco_unit_usd": 2.0, "scenario_unit_price_usd": 1.8, "risk_penalty_usd": 0.03, "failure_probability": 0.08, "Printing Loss %": 7.0, "Lamination Loss %": 5.0, "Slitting Loss %": 2.0})
    low_result = apply_flexible_laminate_risk_to_tco(low, 500000)
    high_result = apply_flexible_laminate_risk_to_tco(high, 500000)
    assert high_result["laminate_failure_probability"] > low_result["laminate_failure_probability"]
    assert high_result["laminate_risk_penalty_usd"] > low_result["laminate_risk_penalty_usd"]
    assert "effective_process_loss_pct" in high_result
    assert "process_loss_risk_penalty_usd" not in high_result


def test_risk_quality_changes_ranking():
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    data.loc[0, "Quoted Unit Price USD"] = 2.10
    data.loc[1, "Quoted Unit Price USD"] = 2.10
    for field in [
        "Substrate Availability %",
        "Printing Capability Score",
        "Lamination Capability Score",
        "Bond Strength Continuity Score",
        "Seal Integrity Continuity Score",
        "Solvent Retention Control Score",
    ]:
        data.loc[0, field] = 95
        data.loc[1, field] = 70
    data.loc[0, "Press Capacity Utilisation %"] = 60
    data.loc[0, "Lamination Capacity Utilisation %"] = 60
    data.loc[1, "Press Capacity Utilisation %"] = 90
    data.loc[1, "Lamination Capacity Utilisation %"] = 90
    scored = enrich_supplier_scores(data, _assumptions())
    assert scored.iloc[0]["Supplier"] == "Precision Flexibles Ltd"


def test_ineligible_supplier_excluded_from_standard_and_optimized_allocation():
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    data.loc[2, "Seal Integrity Continuity Score"] = 60
    scored = enrich_supplier_scores(data, _assumptions())
    assert not bool(scored.loc[scored["Supplier"] == "Circular Laminate Solutions", "technical_eligible"].iloc[0])
    standard = recommend_allocation(scored, 500000, min_risk_score=0, min_esg_score=0)
    optimized = optimize_allocation(scored, 500000)["allocation_df"]
    assert "Circular Laminate Solutions" not in set(standard["Supplier"])
    assert "Circular Laminate Solutions" not in set(optimized["Supplier"])


def test_all_ineligible_returns_no_allocation_and_blocks_recommendation():
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    data["Application Approval Status"] = "Not approved"
    scored = enrich_supplier_scores(data, _assumptions())
    assert not scored["technical_eligible"].any()
    assert recommend_allocation(scored, 500000).empty
    optimized = optimize_allocation(scored, 500000)
    assert optimized["allocation_df"].empty
    assert "No technically eligible" in optimized["explanation"]
    result = validate_scored_output(scored)
    assert not result["is_valid"]
    assert any("No technically eligible supplier" in item for item in result["errors"])


def test_supplier_intelligence_exposes_c2_decision_fields():
    scored = enrich_supplier_scores(get_flexible_laminate_demo_suppliers("PET / PE"), _assumptions())
    columns = set(build_supplier_intelligence(scored, "Packaging Procurement", "Flexible Laminates")["comparison_df"].columns)
    assert {"Technical Eligibility", "Technical Ineligibility Reasons", "Risk Category", "Failure Probability"} <= columns


def test_positive_recommendations_exclude_ineligible_lowest_cost_and_best_performer():
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    data.loc[2, "Quoted Unit Price USD"] = 0.01
    data.loc[2, "OTIF %"] = 100
    data.loc[2, "Quality PPM"] = 0
    data.loc[2, "Application Approval Status"] = "Not approved"
    scored = enrich_supplier_scores(data, _assumptions())
    intelligence = build_supplier_intelligence(scored, "Packaging Procurement", "Flexible Laminates")
    positive = [rec for rec in intelligence["recommendations"] if rec["Recommendation"] in POSITIVE_RECOMMENDATION_ROLES]
    assert all(rec["Supplier"] != "Circular Laminate Solutions" for rec in positive)
    assert next(rec for rec in positive if rec["Recommendation"] == "Lowest Cost Supplier")["Supplier"] != "Circular Laminate Solutions"
    assert next(rec for rec in positive if rec["Recommendation"] == "Best Performer")["Supplier"] != "Circular Laminate Solutions"


def test_all_ineligible_supplier_intelligence_returns_no_qualified_positive_roles():
    data = get_flexible_laminate_demo_suppliers("PET / PE")
    data["Application Approval Status"] = "Not approved"
    scored = enrich_supplier_scores(data, _assumptions())
    intelligence = build_supplier_intelligence(scored, "Packaging Procurement", "Flexible Laminates")
    positive = [rec for rec in intelligence["recommendations"] if rec["Recommendation"] in POSITIVE_RECOMMENDATION_ROLES]
    assert positive
    assert all(rec["Supplier"] == "No Qualified Supplier" for rec in positive)
    assert "No technically eligible supplier" in intelligence["executive_narrative"]


def test_supplier_intelligence_orders_eligible_before_ineligible():
    scored = enrich_supplier_scores(get_flexible_laminate_demo_suppliers("PET / PE"), _assumptions())
    comparison = build_supplier_intelligence(scored, "Packaging Procurement", "Flexible Laminates")["comparison_df"]
    labels = list(comparison["Technical Eligibility"])
    first_ineligible = labels.index("Ineligible") if "Ineligible" in labels else len(labels)
    assert all(label == "Eligible" for label in labels[:first_ineligible])


def test_generic_and_laminate_risk_fields_reconcile():
    scored = enrich_supplier_scores(get_flexible_laminate_demo_suppliers("PET / PE"), _assumptions())
    row = scored.iloc[0]
    assert row["combined_risk_penalty_usd"] == pytest.approx(
        row["generic_risk_penalty_usd"] + row["laminate_risk_penalty_usd"], abs=1e-4
    )
    assert row["adjusted_tco_unit_usd"] == pytest.approx(
        row["base_adjusted_tco_unit_usd"] + row["laminate_risk_penalty_usd"], abs=1e-4
    )
    assert row["generic_failure_probability"] >= 0
    assert row["laminate_failure_probability"] >= 0


@pytest.mark.parametrize("demand_change", [0.20, -0.20])
def test_annual_tco_uses_demand_adjusted_effective_volume(demand_change):
    scored = enrich_supplier_scores(
        get_flexible_laminate_demo_suppliers("PET / PE"),
        _assumptions(demand_change=demand_change),
    )
    row = scored.iloc[0]
    expected_volume = 500000 * (1 + demand_change)
    assert row["effective_annual_volume"] == pytest.approx(expected_volume)
    assert row["annual_tco_usd"] == pytest.approx(
        row["adjusted_tco_unit_usd"] * expected_volume,
        abs=1.0,
    )


def test_executive_risk_output_includes_laminate_controls():
    scored = enrich_supplier_scores(get_flexible_laminate_demo_suppliers("PET / PE"), _assumptions())
    risk = assess_procurement_risks(scored, optimize_allocation(scored, 500000)["allocation_df"])
    names = {item["Risk"] for item in risk["risks"]}
    assert {"Laminate substrate availability", "Laminate technical continuity", "Laminate technical eligibility"} <= names


def test_explicit_structure_isolation_remains_intact():
    first = get_demo_data("Packaging Procurement", "Flexible Laminates", "BOPP / CPP")
    second = get_demo_data("Packaging Procurement", "Flexible Laminates", "PET / PE")
    assert set(first["Laminate Structure"]) == {"BOPP / CPP"}
    assert set(second["Laminate Structure"]) == {"PET / PE"}
    assert validate_rfq_dataframe(second, "Packaging Procurement", "Flexible Laminates", "PET / PE")["is_valid"]


def test_non_regression_existing_categories():
    assert set(get_demo_data("Packaging Procurement", "Corrugated Board")["Unit"]) == {"piece"}
    assert set(get_demo_data("Raw Material Procurement", "Kraft Paper")["Material"]) == {"Kraft Paper"}
    assert set(get_demo_data("Raw Material Procurement", "PET Resin")["Material"]) == {"PET Resin"}
