from __future__ import annotations

import ast
from pathlib import Path

import pandas as pd
import pytest

from modules.data_loader import get_flexible_laminate_demo_suppliers
import modules.multi_supplier_allocation_scenario as scenario_module
from modules.multi_supplier_allocation_route import RouteStatus
from modules.multi_supplier_allocation_scenario import (
    MISSING_EVIDENCE_ORIGIN_REASON,
    MISSING_EVIDENCE_ORIGIN_STATUS,
    SCENARIO_ALLOCATION_VERSION,
    run_scenario_allocation,
)
from modules.scenario_engine import run_flexible_laminate_scenario


SCENARIO_ENGINE_PATH = Path("modules/scenario_engine.py")


def assumptions(**overrides):
    values = {
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
    values.update(overrides)
    return values


def scored_frame():
    return pd.DataFrame(
        [
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
            {
                "Supplier": "Supplier C",
                "technical_eligible": False,
                "adjusted_tco_unit_usd": 0.90,
                "total_score": 95.0,
                "risk_score": 90.0,
                "performance_score": 90.0,
                "esg_score": 90.0,
                "Supplier Capacity": 1000.0,
                "technical_ineligibility_reasons": "Capability gap",
            },
        ]
    )


def test_applicable_scenario_uses_exact_canonical_route_result():
    result = run_scenario_allocation(
        scored_frame(),
        assumptions(),
        scenario_name="Base Case",
        effective_annual_volume=1000.0,
        scenario_assumption_version="TEST-SCENARIO-v1",
        scenario_metadata={"evidence_origin": "controlled_synthetic"},
    )
    assert result.scenario_allocation_version == SCENARIO_ALLOCATION_VERSION
    assert result.scenario_applicable is True
    assert result.route_result is not None
    assert result.route_result.route_status in {RouteStatus.READY, RouteStatus.WARNING}
    assert result.route_result.allocation_result is not None
    assert result.allocation_available is True
    assert result.human_review_required is True
    assert result.legacy_fallback_used is False
    assert result.compatibility_allocation()["allocation_df"].equals(result.allocation_df)
    assert result.compatibility_allocation()["route_status"] == result.route_status


def test_scenario_projection_contains_exact_gate2_values():
    result = run_scenario_allocation(
        scored_frame(),
        assumptions(),
        scenario_name="Base Case",
        effective_annual_volume=1000.0,
        evidence_origin="controlled_synthetic",
    )
    allocation = result.route_result.allocation_result
    assert allocation is not None
    projected = result.allocation_df.set_index("Supplier")
    for supplier_id in allocation.selected_supplier_ids:
        display_name = next(name for name in projected.index if str(name).casefold() == supplier_id)
        row = projected.loc[display_name]
        assert row["Recommended Allocation %"] == allocation.allocation_pct_by_supplier[supplier_id]
        assert row["Allocated Volume"] == allocation.allocated_volume_by_supplier[supplier_id]
        assert row["Estimated Annual TCO USD"] == allocation.annual_tco_by_supplier[supplier_id]
        assert row["Capacity Utilization %"] == allocation.capacity_utilization_pct_by_supplier[supplier_id]


def test_missing_capacity_fails_closed_without_legacy_fallback():
    result = run_scenario_allocation(
        scored_frame().drop(columns=["Supplier Capacity"]),
        assumptions(),
        scenario_name="Capacity Missing",
        effective_annual_volume=1000.0,
        evidence_origin="controlled_synthetic",
    )
    assert result.route_result is not None
    assert result.route_result.route_status is RouteStatus.BLOCKED_MISSING_CAPACITY
    assert result.route_result.allocation_result is None
    assert result.allocation_df.empty
    assert result.allocation_available is False
    assert result.legacy_fallback_used is False
    assert result.compatibility_allocation()["allocation_df"].empty


@pytest.mark.parametrize("origin", [None, "", "   "])
def test_applicable_scenario_without_explicit_evidence_origin_fails_closed(monkeypatch, origin):
    def unexpected_route_call(*args, **kwargs):
        raise AssertionError("Canonical route must not be invoked without scenario evidence origin")

    monkeypatch.setattr(scenario_module, "run_multi_supplier_allocation_route", unexpected_route_call)
    metadata = {} if origin is None else {"evidence_origin": origin}
    result = run_scenario_allocation(
        scored_frame(),
        assumptions(),
        scenario_name="Missing Evidence Origin",
        effective_annual_volume=1000.0,
        scenario_metadata=metadata,
    )
    assert result.scenario_applicable is True
    assert result.route_result is None
    assert result.route_status == MISSING_EVIDENCE_ORIGIN_STATUS
    assert result.integration_blocking_reasons == (MISSING_EVIDENCE_ORIGIN_REASON,)
    assert result.allocation_df.empty
    assert result.allocation_available is False
    assert result.human_review_required is True
    assert result.legacy_fallback_used is False
    compatibility = result.compatibility_allocation()
    assert compatibility["allocation_df"].empty
    assert compatibility["blocking_reasons"] == (MISSING_EVIDENCE_ORIGIN_REASON,)
    assert compatibility["evidence_origin"] == ""


@pytest.mark.parametrize("origin", ["controlled_synthetic", "supplied", "governed_workbook"])
def test_explicit_supported_evidence_origin_is_retained(origin):
    result = run_scenario_allocation(
        scored_frame(),
        assumptions(),
        scenario_name="Explicit Evidence",
        effective_annual_volume=1000.0,
        evidence_origin=f"  {origin}  ",
    )
    assert result.route_result is not None
    assert result.route_result.evidence_origin == origin
    assert result.compatibility_allocation()["evidence_origin"] == origin
    assert result.human_review_required is True
    assert result.legacy_fallback_used is False


def test_unsupported_explicit_evidence_origin_remains_rejected():
    result = run_scenario_allocation(
        scored_frame(),
        assumptions(),
        scenario_name="Unsupported Evidence",
        effective_annual_volume=1000.0,
        evidence_origin="unverified_external",
    )
    assert result.route_result is not None
    assert result.route_result.allocation_result is None
    assert result.allocation_df.empty
    assert result.allocation_available is False
    assert result.human_review_required is True
    assert result.legacy_fallback_used is False
    assert any("Unsupported evidence_origin" in reason for reason in result.route_result.blocking_reasons)


def test_non_applicable_scenario_does_not_invoke_route(monkeypatch):
    def unexpected_route_call(*args, **kwargs):
        raise AssertionError("Non-applicable scenario must not invoke canonical route")

    monkeypatch.setattr(scenario_module, "run_multi_supplier_allocation_route", unexpected_route_call)
    result = run_scenario_allocation(
        scored_frame(),
        assumptions(),
        scenario_name="Not Applicable",
        effective_annual_volume=1000.0,
        scenario_applicable=False,
        scenario_assumption_version="TEST-SCENARIO-v1",
    )
    assert result.scenario_applicable is False
    assert result.route_result is None
    assert result.route_status == "NOT_APPLICABLE"
    assert result.allocation_df.empty
    assert result.compatibility_allocation()["legacy_fallback_used"] is False


def test_display_currency_never_changes_scenario_allocation():
    usd = run_scenario_allocation(
        scored_frame(),
        assumptions(display_currency="USD"),
        scenario_name="Base",
        effective_annual_volume=1000.0,
        evidence_origin="controlled_synthetic",
    )
    inr = run_scenario_allocation(
        scored_frame(),
        assumptions(display_currency="INR"),
        scenario_name="Base",
        effective_annual_volume=1000.0,
        evidence_origin="controlled_synthetic",
    )
    both = run_scenario_allocation(
        scored_frame(),
        assumptions(display_currency="Both"),
        scenario_name="Base",
        effective_annual_volume=1000.0,
        evidence_origin="controlled_synthetic",
    )
    assert usd.route_result.to_json() == inr.route_result.to_json()
    assert usd.route_result.to_json() == both.route_result.to_json()


def test_flexible_laminate_scenario_exposes_one_canonical_allocation():
    laminate_assumptions = {
        "category": "Packaging Procurement",
        "commodity": "Flexible Laminates",
        "laminate_structure": "PET / PE",
        "annual_volume": 500000,
        "annual_volume_unit": "kg",
        "raw_material_shock": 0.0,
        "freight_shock": 0.0,
        "demand_change": 0.0,
        "fx_rate": 83.0,
        "category_profile": {"unit": "kg"},
    }
    result = run_flexible_laminate_scenario(
        get_flexible_laminate_demo_suppliers("PET / PE"),
        laminate_assumptions,
        "Base Case",
    )
    scenario_allocation = result["scenario_allocation"]
    assert result["standard_allocation_df"].equals(scenario_allocation.allocation_df)
    assert result["optimized_allocation"]["allocation_df"].equals(scenario_allocation.allocation_df)
    assert result["optimized_allocation"]["legacy_fallback_used"] is False


def test_scenario_engine_never_imports_or_calls_legacy_allocation_functions():
    tree = ast.parse(SCENARIO_ENGINE_PATH.read_text(encoding="utf-8"))
    imports = {
        node.module: {alias.name for alias in node.names}
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert "modules.allocation" not in imports
    assert "modules.allocation_optimizer" not in imports
    assert "recommend_allocation" not in called_names
    assert "optimize_allocation" not in called_names
    assert "run_scenario_allocation" in imports["modules.multi_supplier_allocation_scenario"]
