from __future__ import annotations

from dataclasses import replace

import pandas as pd

from modules.multi_supplier_allocation_application import (
    ALLOCATION_COLUMNS,
    APPLICATION_INTEGRATION_VERSION,
    build_application_route_controls,
    build_route_decision_control,
    resolve_application_source_type,
    route_allows_allocation,
    run_application_allocation,
)
from modules.multi_supplier_allocation_route import RouteStatus


def assumptions(**overrides):
    values = {
        "data_source": "Synthetic Demo",
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


def eligible_validation(**overrides):
    values = {
        "recommendation_allowed": True,
        "final_award_language_allowed": True,
    }
    values.update(overrides)
    return values


def test_controls_are_explicit_and_use_canonical_comparison_currency():
    controls = build_application_route_controls(assumptions())
    assert controls == {
        "annual_volume": 1000.0,
        "annual_volume_unit": "kg",
        "required_awardee_count": 2,
        "minimum_awarded_share_pct": 10.0,
        "maximum_supplier_share_pct": 60.0,
        "minimum_continuity_share_pct": 20.0,
        "minimum_risk_score": 55.0,
        "minimum_esg_score": 50.0,
        "capacity_utilization_ceiling_pct": 90.0,
        "category": "Raw Material Procurement",
        "commodity": "PET Resin",
        "comparison_currency": "USD",
        "required_supplier_ids": (),
        "excluded_supplier_ids": (),
    }


def test_source_type_resolution_is_deterministic():
    assert resolve_application_source_type(assumptions()) == ("synthetic_demo", "controlled_synthetic")
    assert resolve_application_source_type(assumptions(data_source="Upload RFQ CSV/Excel")) == (
        "uploaded_rfq",
        "supplied",
    )
    assert resolve_application_source_type(
        assumptions(data_source="Governed v1.3 Workbook Review Preview")
    ) == ("governed_workbook", "governed_workbook")
    assert resolve_application_source_type(assumptions(commodity="Steel")) == (
        "steel_synthetic",
        "controlled_synthetic",
    )


def test_application_bundle_uses_one_exact_canonical_result():
    bundle = run_application_allocation(scored_frame(), assumptions())
    assert bundle.integration_version == APPLICATION_INTEGRATION_VERSION
    assert bundle.route_result.route_status in {RouteStatus.READY, RouteStatus.WARNING}
    assert bundle.route_result.allocation_result is not None
    assert tuple(bundle.allocation_df.columns) == ALLOCATION_COLUMNS
    assert bundle.intelligence_allocation["allocation_df"].equals(bundle.allocation_df)
    assert bundle.intelligence_allocation["route_status"] == bundle.route_result.route_status.value
    assert bundle.intelligence_allocation["legacy_fallback_used"] is False
    assert bundle.scenario_allocation_deferred is True


def test_projection_uses_engine_values_without_recalculation():
    bundle = run_application_allocation(scored_frame(), assumptions())
    allocation = bundle.route_result.allocation_result
    assert allocation is not None
    projected = bundle.allocation_df.set_index("Supplier")
    for supplier_id in allocation.selected_supplier_ids:
        display_name = next(name for name in projected.index if str(name).casefold() == supplier_id)
        row = projected.loc[display_name]
        assert row["Recommended Allocation %"] == allocation.allocation_pct_by_supplier[supplier_id]
        assert row["Advanced TCO Unit USD"] == allocation.unit_tco_by_supplier[supplier_id]
        assert row["Estimated Annual TCO USD"] == allocation.annual_tco_by_supplier[supplier_id]
        assert row["Allocated Volume"] == allocation.allocated_volume_by_supplier[supplier_id]
        assert row["Capacity Utilization %"] == allocation.capacity_utilization_pct_by_supplier[supplier_id]


def test_ineligible_supplier_never_enters_application_projection():
    bundle = run_application_allocation(scored_frame(), assumptions())
    assert "Supplier C" not in set(bundle.allocation_df["Supplier"])


def test_missing_capacity_fails_closed_for_every_consumer():
    data = scored_frame().drop(columns=["Supplier Capacity"])
    bundle = run_application_allocation(data, assumptions())
    assert bundle.route_result.route_status is RouteStatus.BLOCKED_MISSING_CAPACITY
    assert bundle.route_result.allocation_result is None
    assert bundle.allocation_df.empty
    assert bundle.intelligence_allocation["allocation_df"].empty
    assert bundle.intelligence_allocation["human_review_required"] is True


def test_blocked_route_overrides_otherwise_eligible_recommendation_controls():
    data = scored_frame().drop(columns=["Supplier Capacity"])
    bundle = run_application_allocation(data, assumptions())
    control = build_route_decision_control(bundle.route_result, eligible_validation())
    assert control["route_allows_allocation"] is False
    assert control["eligibility_allows_recommendation"] is True
    assert control["recommendation_language_allowed"] is False
    assert control["final_award_language_allowed"] is False
    assert control["analytical_only"] is True
    assert "no supplier award or allocation recommendation is permitted" in control["message"]


def test_ready_and_warning_routes_allow_human_reviewed_recommendation_language():
    bundle = run_application_allocation(scored_frame(), assumptions())
    assert route_allows_allocation(bundle.route_result) is True
    ready = build_route_decision_control(bundle.route_result, eligible_validation())
    assert ready["recommendation_language_allowed"] is True
    assert ready["final_award_language_allowed"] is True

    warning_result = replace(
        bundle.route_result,
        route_status=RouteStatus.WARNING,
        warnings=("Human review warning",),
    )
    warning = build_route_decision_control(warning_result, eligible_validation())
    assert route_allows_allocation(warning_result) is True
    assert warning["recommendation_language_allowed"] is True
    assert warning["final_award_language_allowed"] is True


def test_eligibility_can_still_withhold_language_when_route_is_ready():
    bundle = run_application_allocation(scored_frame(), assumptions())
    control = build_route_decision_control(
        bundle.route_result,
        eligible_validation(recommendation_allowed=False, final_award_language_allowed=False),
    )
    assert control["route_allows_allocation"] is True
    assert control["recommendation_language_allowed"] is False
    assert control["final_award_language_allowed"] is False


def test_display_currency_is_not_an_allocation_input():
    usd = run_application_allocation(scored_frame(), assumptions(display_currency="USD"))
    inr = run_application_allocation(scored_frame(), assumptions(display_currency="INR"))
    both = run_application_allocation(scored_frame(), assumptions(display_currency="Both"))
    assert usd.route_result.allocation_result.to_json() == inr.route_result.allocation_result.to_json()
    assert usd.route_result.allocation_result.to_json() == both.route_result.allocation_result.to_json()


def test_control_summary_discloses_all_material_route_controls():
    bundle = run_application_allocation(
        scored_frame(),
        assumptions(required_supplier_ids=("supplier a",), excluded_supplier_ids=("supplier c",)),
    )
    summary = dict(bundle.control_summary)
    assert summary == {
        "Required awardees": 2,
        "Minimum awarded share %": 10.0,
        "Maximum supplier share %": 60.0,
        "Minimum continuity share %": 20.0,
        "Minimum risk score": 55.0,
        "Minimum ESG score": 50.0,
        "Capacity utilization ceiling %": 90.0,
        "Required supplier IDs": "supplier a",
        "Excluded supplier IDs": "supplier c",
        "Comparison currency": "USD",
        "Evidence origin": "controlled_synthetic",
        "Human review required": True,
        "Legacy fallback used": False,
    }


def test_control_summary_uses_none_for_empty_supplier_constraints():
    bundle = run_application_allocation(scored_frame(), assumptions())
    summary = dict(bundle.control_summary)
    assert summary["Required supplier IDs"] == "None"
    assert summary["Excluded supplier IDs"] == "None"
