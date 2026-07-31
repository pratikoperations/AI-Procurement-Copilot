import math

import pandas as pd
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
from modules.validation import validate_rfq_dataframe, validate_scored_output


def _assumptions(structure="PET / PE"):
    return {
        "category":"Packaging Procurement","commodity":"Flexible Laminates",
        "laminate_structure":structure,"annual_volume":500000,"raw_material_shock":0,
        "freight_shock":0,"demand_change":0,"fx_rate":83,
    }


def _eligible_record():
    return get_flexible_laminate_demo_suppliers("PET / PE").iloc[0].to_dict()


@pytest.mark.parametrize("field,(minimum,maximum)", ELIGIBILITY_THRESHOLDS.items())
def test_each_eligibility_threshold_boundary_passes(field, minimum, maximum):
    record=_eligible_record()
    record[field]=minimum if minimum is not None else maximum
    assert assess_flexible_laminate_supplier(record)["technical_eligible"]


@pytest.mark.parametrize("field,(minimum,maximum)", ELIGIBILITY_THRESHOLDS.items())
def test_each_eligibility_threshold_breach_fails(field, minimum, maximum):
    record=_eligible_record()
    record[field]=(minimum-0.1) if minimum is not None else (maximum+0.1)
    result=assess_flexible_laminate_supplier(record)
    assert not result["technical_eligible"]
    assert any(field in reason for reason in result["technical_ineligibility_reasons"])


@pytest.mark.parametrize("value", [float("nan"),float("inf"),float("-inf")])
def test_non_finite_risk_inputs_fail_closed(value):
    record=_eligible_record(); record["Substrate Availability %"]=value
    with pytest.raises(ValueError,match="finite"):
        assess_flexible_laminate_supplier(record)


def test_invalid_risk_range_fails_validation():
    data=get_flexible_laminate_demo_suppliers("PET / PE")
    data.loc[0,"Bond Strength Continuity Score"]=101
    result=validate_flexible_laminate_dataframe(data,"PET / PE")
    assert not result["is_valid"]
    assert any("Bond Strength" in item for item in result["errors"])


def test_application_approval_controls_eligibility():
    record=_eligible_record(); record["Application Approval Status"]="Conditional"
    assert not assess_flexible_laminate_supplier(record)["technical_eligible"]


def test_existing_tooling_controls_eligibility():
    record=_eligible_record(); record["Tooling Status"]="Existing"; record["Tooling Availability"]="Not assessed"
    assert not assess_flexible_laminate_supplier(record)["technical_eligible"]


def test_process_loss_affects_risk_and_tco():
    low=_eligible_record(); high=dict(low)
    low.update({"adjusted_tco_unit_usd":2.0,"Printing Loss %":1.0,"Lamination Loss %":1.0,"Slitting Loss %":0.5})
    high.update({"adjusted_tco_unit_usd":2.0,"Printing Loss %":7.0,"Lamination Loss %":5.0,"Slitting Loss %":2.0})
    low_result=apply_flexible_laminate_risk_to_tco(low,500000)
    high_result=apply_flexible_laminate_risk_to_tco(high,500000)
    assert high_result["failure_probability"] > low_result["failure_probability"]
    assert high_result["adjusted_tco_unit_usd"] > low_result["adjusted_tco_unit_usd"]


def test_risk_quality_changes_ranking():
    data=get_flexible_laminate_demo_suppliers("PET / PE")
    data.loc[0,"Quoted Unit Price USD"]=2.10
    data.loc[1,"Quoted Unit Price USD"]=2.10
    for field in ["Substrate Availability %","Printing Capability Score","Lamination Capability Score","Bond Strength Continuity Score","Seal Integrity Continuity Score","Solvent Retention Control Score"]:
        data.loc[0,field]=95; data.loc[1,field]=70
    data.loc[0,"Press Capacity Utilisation %"]=60; data.loc[0,"Lamination Capacity Utilisation %"]=60
    data.loc[1,"Press Capacity Utilisation %"]=90; data.loc[1,"Lamination Capacity Utilisation %"]=90
    scored=enrich_supplier_scores(data,_assumptions())
    assert scored.iloc[0]["Supplier"]=="Precision Flexibles Ltd"
    assert scored.iloc[0]["risk_score"] > scored.loc[scored["Supplier"]=="BarrierPack Films","risk_score"].iloc[0]


def test_ineligible_supplier_excluded_from_standard_and_optimized_allocation():
    data=get_flexible_laminate_demo_suppliers("PET / PE")
    data.loc[2,"Seal Integrity Continuity Score"]=60
    scored=enrich_supplier_scores(data,_assumptions())
    blocked=scored.loc[scored["Supplier"]=="Circular Laminate Solutions"].iloc[0]
    assert not bool(blocked["technical_eligible"])
    standard=recommend_allocation(scored,500000,min_risk_score=0,min_esg_score=0)
    optimized=optimize_allocation(scored,500000)["allocation_df"]
    assert "Circular Laminate Solutions" not in set(standard["Supplier"])
    assert "Circular Laminate Solutions" not in set(optimized["Supplier"])


def test_all_ineligible_returns_no_allocation_and_blocks_recommendation():
    data=get_flexible_laminate_demo_suppliers("PET / PE")
    data["Application Approval Status"]="Not approved"
    scored=enrich_supplier_scores(data,_assumptions())
    assert not scored["technical_eligible"].any()
    assert recommend_allocation(scored,500000).empty
    optimized=optimize_allocation(scored,500000)
    assert optimized["allocation_df"].empty
    assert "No technically eligible" in optimized["explanation"]
    output_validation=validate_scored_output(scored)
    assert not output_validation["is_valid"]
    assert any("No technically eligible supplier" in item for item in output_validation["errors"])


def test_supplier_intelligence_exposes_c2_decision_fields():
    scored=enrich_supplier_scores(get_flexible_laminate_demo_suppliers("PET / PE"),_assumptions())
    result=build_supplier_intelligence(scored,"Packaging Procurement","Flexible Laminates")
    columns=set(result["comparison_df"].columns)
    assert {"Technical Eligibility","Technical Ineligibility Reasons","Risk Category","Failure Probability"} <= columns


def test_executive_risk_output_includes_laminate_controls():
    scored=enrich_supplier_scores(get_flexible_laminate_demo_suppliers("PET / PE"),_assumptions())
    risk=assess_procurement_risks(scored,optimize_allocation(scored,500000)["allocation_df"])
    names={item["Risk"] for item in risk["risks"]}
    assert "Laminate substrate availability" in names
    assert "Laminate technical continuity" in names
    assert "Laminate technical eligibility" in names


def test_explicit_structure_isolation_remains_intact():
    first=get_demo_data("Packaging Procurement","Flexible Laminates","BOPP / CPP")
    second=get_demo_data("Packaging Procurement","Flexible Laminates","PET / PE")
    assert set(first["Laminate Structure"])=={"BOPP / CPP"}
    assert set(second["Laminate Structure"])=={"PET / PE"}
    assert validate_rfq_dataframe(second,"Packaging Procurement","Flexible Laminates","PET / PE")["is_valid"]


def test_non_regression_existing_categories():
    assert set(get_demo_data("Packaging Procurement","Corrugated Board")["Unit"])=={"piece"}
    assert set(get_demo_data("Raw Material Procurement","Kraft Paper")["Material"])=={"Kraft Paper"}
    assert set(get_demo_data("Raw Material Procurement","PET Resin")["Material"])=={"PET Resin"}
