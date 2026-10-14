"""LOGISTICS-2 governed carrier performance and risk evaluation tests."""

import pytest

from modules.commodity_library import get_commodity_profile
from modules.logistics_engine import CATEGORY_NAME, FIRST_COMMODITY
from modules.logistics_performance import (
    CARRIER_EVALUATION_VERSION,
    PERFORMANCE_POLICY_CONTRACT,
    evaluate_carrier_performance,
    get_carrier_evaluation_profile,
)


POLICY = {
    "maximum_transit_time_days": 2,
    "minimum_otif_pct": 95,
    "maximum_damage_claim_rate_pct": 1.0,
    "require_capacity_confirmation": True,
    "accepted_compliance_statuses": ("Meets Requirement",),
}

VERIFIED_EVIDENCE = {
    "capacity_confirmed": True,
    "transit_time_days": 1,
    "otif_pct": 97,
    "damage_claim_rate_pct": 0.4,
    "compliance_status": "Meets Requirement",
    "evidence_status": "Verified by Human Review",
    "source_label": "Buyer-reviewed carrier KPI pack",
}


def test_logistics_2_profile_is_bounded_and_non_ranking():
    profile = get_carrier_evaluation_profile()

    assert profile["contract_version"] == CARRIER_EVALUATION_VERSION == "LOGISTICS-2"
    assert profile["engine_status"] == "Foundation Preview"
    assert profile["composite_score_enabled"] is False
    assert profile["carrier_ranking_enabled"] is False
    assert profile["allocation_enabled"] is False
    assert profile["route_optimization_enabled"] is False
    assert profile["award_recommendation_enabled"] is False
    assert profile["human_approval_required"] is True


def test_commodity_metadata_registers_logistics_2_contract():
    profile = get_commodity_profile(CATEGORY_NAME, FIRST_COMMODITY)

    assert profile["carrier_evaluation_contract_version"] == "LOGISTICS-2"
    assert profile["carrier_evaluation_dimensions"] == [
        "capacity confirmation",
        "transit time",
        "OTIF",
        "damage / claims",
        "compliance evidence",
        "evidence quality",
    ]


def test_verified_carrier_meeting_policy_is_eligible_for_human_review_only():
    result = evaluate_carrier_performance(
        carrier_id="LOG-C-001",
        carrier_name="Synthetic Carrier A",
        performance_evidence=VERIFIED_EVIDENCE,
        buyer_policy=POLICY,
    )

    assert result["overall_status"] == "MEETS_BUYER_POLICY_FOR_HUMAN_REVIEW"
    assert result["policy_breach_count"] == 0
    assert result["review_flag_count"] == 0
    assert result["risk_flags"] == []
    assert all(item["status"] == "PASS" for item in result["criteria"])
    assert result["human_approval_required"] is True


def test_unverified_evidence_is_explicitly_flagged_without_failing_policy_math():
    evidence = dict(VERIFIED_EVIDENCE)
    evidence["evidence_status"] = "Supplied — Unverified"
    evidence["source_label"] = "Supplier-submitted KPI pack"

    result = evaluate_carrier_performance(
        carrier_id="LOG-C-002",
        carrier_name="Synthetic Carrier B",
        performance_evidence=evidence,
        buyer_policy=POLICY,
    )

    assert result["overall_status"] == "MEETS_POLICY_WITH_UNVERIFIED_EVIDENCE"
    assert result["policy_breach_count"] == 0
    assert result["review_flag_count"] == 1
    assert "compliance, safety, and evidence-quality risk" in result["risk_flags"]
    evidence_quality = [item for item in result["criteria"] if item["criterion"] == "evidence quality"][0]
    assert evidence_quality["status"] == "REVIEW"


def test_policy_breaches_are_exposed_as_criteria_not_hidden_score():
    evidence = dict(VERIFIED_EVIDENCE)
    evidence.update(
        {
            "capacity_confirmed": False,
            "transit_time_days": 3,
            "otif_pct": 90,
            "damage_claim_rate_pct": 1.8,
            "compliance_status": "Human Review Required",
        }
    )

    result = evaluate_carrier_performance(
        carrier_id="LOG-C-003",
        carrier_name="Synthetic Carrier C",
        performance_evidence=evidence,
        buyer_policy=POLICY,
    )

    assert result["overall_status"] == "DOES_NOT_MEET_BUYER_POLICY"
    assert result["policy_breach_count"] == 5
    assert result["review_flag_count"] == 0
    assert result["composite_score"] is None
    assert result["rank"] is None
    assert result["ranking_performed"] is False
    assert result["award_recommendation_created"] is False
    assert len(result["risk_flags"]) >= 4


@pytest.mark.parametrize(
    ("override", "message"),
    [
        ({"maximum_transit_time_days": None}, "Missing buyer policy fields"),
        ({"minimum_otif_pct": 101}, "between zero and 100"),
        ({"maximum_damage_claim_rate_pct": -1}, "zero or greater"),
        ({"require_capacity_confirmation": "yes"}, "must be a boolean"),
        ({"accepted_compliance_statuses": ()}, "non-empty sequence"),
    ],
)
def test_policy_contract_fails_closed_without_invented_defaults(override, message):
    policy = {**POLICY, **override}

    with pytest.raises(ValueError, match=message):
        evaluate_carrier_performance(
            carrier_id="LOG-C-004",
            carrier_name="Synthetic Carrier D",
            performance_evidence=VERIFIED_EVIDENCE,
            buyer_policy=policy,
        )


@pytest.mark.parametrize(
    ("override", "message"),
    [
        ({"capacity_confirmed": None}, "Missing carrier performance evidence fields"),
        ({"capacity_confirmed": "yes"}, "must be a boolean"),
        ({"transit_time_days": -1}, "zero or greater"),
        ({"otif_pct": 101}, "between zero and 100"),
        ({"damage_claim_rate_pct": -0.1}, "zero or greater"),
        ({"compliance_status": " "}, "must not be blank"),
        ({"evidence_status": "Unknown"}, "Unsupported evidence status"),
        ({"source_label": " "}, "Source label is required"),
    ],
)
def test_carrier_evidence_contract_fails_closed(override, message):
    evidence = {**VERIFIED_EVIDENCE, **override}

    with pytest.raises(ValueError, match=message):
        evaluate_carrier_performance(
            carrier_id="LOG-C-005",
            carrier_name="Synthetic Carrier E",
            performance_evidence=evidence,
            buyer_policy=POLICY,
        )


def test_identity_is_mandatory():
    with pytest.raises(ValueError, match="carrier_id is required"):
        evaluate_carrier_performance(
            carrier_id="",
            carrier_name="Synthetic Carrier",
            performance_evidence=VERIFIED_EVIDENCE,
            buyer_policy=POLICY,
        )

    with pytest.raises(ValueError, match="carrier_name is required"):
        evaluate_carrier_performance(
            carrier_id="LOG-C-006",
            carrier_name="",
            performance_evidence=VERIFIED_EVIDENCE,
            buyer_policy=POLICY,
        )


def test_no_external_data_ranking_allocation_or_award_is_claimed():
    result = evaluate_carrier_performance(
        carrier_id="LOG-C-007",
        carrier_name="Synthetic Carrier F",
        performance_evidence=VERIFIED_EVIDENCE,
        buyer_policy=POLICY,
    )

    assert result["external_data_used"] is False
    assert result["ranking_performed"] is False
    assert result["allocation_performed"] is False
    assert result["route_optimization_performed"] is False
    assert result["award_recommendation_created"] is False
    assert "weights" not in PERFORMANCE_POLICY_CONTRACT
    assert "default_thresholds" not in PERFORMANCE_POLICY_CONTRACT
