"""Export and handoff regression tests."""

import json

from modules.allocation import recommend_allocation
from modules.data_loader import get_demo_suppliers
from modules.exports import (
    build_decision_package_json,
    build_excel_workbook,
    dataframe_to_csv_bytes,
    text_to_bytes,
)
from modules.recommendation import executive_value_breakdown
from modules.scenario import run_scenario_table
from modules.scoring import enrich_supplier_scores
from modules.should_cost import calculate_packaging_should_cost, should_cost_dataframe


ASSUMPTIONS = {
    "annual_volume": 500000,
    "raw_material_shock": 0.0,
    "freight_shock": 0.0,
    "demand_change": 0.0,
    "max_supplier_share": 75,
    "min_backup_share": 25,
    "min_risk_score": 55,
    "min_esg_score": 50,
}


def _build_outputs():
    suppliers = get_demo_suppliers()
    scored = enrich_supplier_scores(suppliers, ASSUMPTIONS)
    should_cost = calculate_packaging_should_cost()
    should_cost_df = should_cost_dataframe(
        should_cost,
        annual_volume=ASSUMPTIONS["annual_volume"],
        fx_rate=83,
    )
    allocation = recommend_allocation(
        scored,
        annual_volume=ASSUMPTIONS["annual_volume"],
        max_supplier_share=ASSUMPTIONS["max_supplier_share"],
        min_backup_share=ASSUMPTIONS["min_backup_share"],
        min_risk_score=ASSUMPTIONS["min_risk_score"],
        min_esg_score=ASSUMPTIONS["min_esg_score"],
    )
    scenarios = run_scenario_table(suppliers, ASSUMPTIONS)
    values = executive_value_breakdown(
        scored,
        ASSUMPTIONS["annual_volume"],
        should_cost["target_unit_cost_usd"],
    )
    return scored, should_cost_df, allocation, scenarios, values


def test_csv_and_text_exports_are_non_empty_bytes():
    scored, _, _, _, _ = _build_outputs()
    assert len(dataframe_to_csv_bytes(scored)) > 100
    assert text_to_bytes("Executive recommendation") == b"Executive recommendation"


def test_json_decision_package_is_valid():
    scored, _, allocation, scenarios, values = _build_outputs()
    payload = build_decision_package_json(
        scored.iloc[0],
        values,
        allocation,
        scenarios,
        {"annual_saving_usd": 1000.0},
    )
    decoded = json.loads(payload.decode("utf-8"))
    assert decoded["recommended_supplier"]["Supplier"]
    assert len(decoded["allocation"]) >= 1
    assert len(decoded["scenarios"]) >= 1


def test_excel_workbook_is_generated():
    scored, should_cost_df, allocation, scenarios, _ = _build_outputs()
    workbook = build_excel_workbook(scored, should_cost_df, allocation, scenarios)
    assert workbook[:2] == b"PK"
    assert len(workbook) > 1000
