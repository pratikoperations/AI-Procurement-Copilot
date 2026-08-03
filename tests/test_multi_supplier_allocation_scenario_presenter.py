from __future__ import annotations

import pandas as pd

from modules.multi_supplier_allocation_scenario import run_scenario_allocation
from modules.multi_supplier_allocation_scenario_presenter import (
    SCENARIO_PRESENTER_VERSION,
    build_scenario_presentation,
)


def _assumptions():
    return {
        "category": "Raw Material Procurement",
        "commodity": "PET Resin",
        "annual_volume": 1000.0,
        "annual_volume_unit": "kg",
        "required_awardee_count": 2,
        "minimum_awarded_share_pct": 10.0,
        "max_supplier_share": 60.0,
        "min_backup_share": 20.0,
        "min_risk_score": 55.0,
        "min_esg_score": 50.0,
        "capacity_utilization_ceiling_pct": 90.0,
    }


def _scored():
    return pd.DataFrame([
        {
            "Supplier": "Supplier A",
            "technical_eligible": True,
            "adjusted_tco_unit_usd": 1.00,
            "total_score": 92.0,
            "risk_score": 82.0,
            "performance_score": 88.0,
            "esg_score": 78.0,
            "Supplier Capacity": 900.0,
        },
        {
            "Supplier": "Supplier B",
            "technical_eligible": True,
            "adjusted_tco_unit_usd": 1.05,
            "total_score": 89.0,
            "risk_score": 79.0,
            "performance_score": 85.0,
            "esg_score": 75.0,
            "Supplier Capacity": 800.0,
        },
    ])


def test_presenter_projects_exact_canonical_allocation_without_calculation():
    result = run_scenario_allocation(
        _scored(),
        _assumptions(),
        scenario_name="Base Case",
        effective_annual_volume=1000.0,
        scenario_assumption_version="TEST-v1",
        evidence_origin="controlled_synthetic",
    )
    presentation = build_scenario_presentation(
        result,
        analytical_leading_supplier="Supplier A",
        analytical_leading_score=92.0,
    )
    assert presentation.presenter_version == SCENARIO_PRESENTER_VERSION
    assert presentation.allocation_available is True
    assert presentation.allocation_df.equals(result.allocation_df)
    assert presentation.route_status in {"READY", "WARNING"}
    assert presentation.human_review_required is True
    assert presentation.legacy_fallback_used is False
    row = presentation.table_row()
    assert row["Canonical Allocation Status"] == "Allocated"
    assert row["Selected Suppliers"]
    assert row["Allocation Shares"]
    assert row["Analytical Leading Supplier"] == "Supplier A"
    assert "Standard Allocation Status" not in row
    assert "Optimized Allocation Status" not in row


def test_presenter_blocks_allocation_when_capacity_is_missing():
    result = run_scenario_allocation(
        _scored().drop(columns=["Supplier Capacity"]),
        _assumptions(),
        scenario_name="Capacity Missing",
        effective_annual_volume=1000.0,
        evidence_origin="controlled_synthetic",
    )
    presentation = build_scenario_presentation(result)
    assert presentation.allocation_available is False
    assert presentation.allocation_df.empty
    assert presentation.blocking_reasons
    row = presentation.table_row()
    assert row["Canonical Allocation Status"] == "No allocation"
    assert row["Selected Suppliers"] == ""
    assert row["Human Review Required"] == "Yes"
    assert row["Legacy Fallback Used"] == "No"


def test_presenter_distinguishes_non_applicable_from_blocked():
    result = run_scenario_allocation(
        _scored(),
        _assumptions(),
        scenario_name="Not Applicable",
        effective_annual_volume=1000.0,
        scenario_applicable=False,
        scenario_assumption_version="TEST-v1",
        scenario_metadata={"reason": "Structure does not use MetPET."},
    )
    presentation = build_scenario_presentation(result)
    assert presentation.route_status == "NOT_APPLICABLE"
    assert presentation.scenario_applicable is False
    assert presentation.blocking_reasons == ()
    assert presentation.status_reason == "Structure does not use MetPET."
    assert presentation.allocation_df.empty


def test_presenter_keeps_analytical_leader_separate_from_allocation():
    result = run_scenario_allocation(
        _scored(),
        _assumptions(),
        scenario_name="Base Case",
        effective_annual_volume=1000.0,
        evidence_origin="controlled_synthetic",
    )
    presentation = build_scenario_presentation(
        result,
        analytical_leading_supplier="Supplier A",
        analytical_leading_score=92.0,
    )
    row = presentation.table_row()
    assert row["Analytical Leading Supplier"] == "Supplier A"
    assert row["Selected Suppliers"]
    assert "Award" not in " ".join(row.keys())
