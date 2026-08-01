"""Read-only trace adapters for representative authoritative paths."""
from __future__ import annotations
from copy import deepcopy

from modules.calculation_trace import IntermediateStep, build_trace


def _authoritative_steps(result):
    if isinstance(result, dict):
        components = result.get("components") or result.get("component_values")
        if isinstance(components, dict):
            return tuple(IntermediateStep(str(k), v, result.get("unit")) for k, v in components.items())
    return (IntermediateStep("intermediate values", available=False, note="Authoritative service did not expose intermediate values."),)


def build_should_cost_trace(*, calculation_id, formula_id, category, inputs, authoritative_result, resolutions=(), supplier=None, rfq_scenario=None, formula_version="1.0"):
    """Adapt Kraft, Flexible Laminates or Steel should-cost output without recalculation."""
    preserved = deepcopy(authoritative_result)
    return build_trace(
        calculation_id=calculation_id,
        formula_id=formula_id,
        formula_version=formula_version,
        category=category,
        supplier=supplier,
        rfq_scenario=rfq_scenario,
        input_snapshot=deepcopy(inputs),
        raw_output=preserved,
        resolutions=tuple(resolutions),
        intermediate_steps=_authoritative_steps(authoritative_result),
        recommendation_impact="Should-cost evidence only; no autonomous award.",
        configuration_versions={"formula": formula_version},
    )


def build_supplier_score_trace(*, inputs, authoritative_result, resolutions=(), supplier=None, weight_profile_version="1.0"):
    preserved = deepcopy(authoritative_result)
    contribution = None
    if isinstance(authoritative_result, dict):
        contribution = authoritative_result.get("weighted_contribution")
    return build_trace(
        calculation_id="SCR-001",
        formula_id="F-SCORE-GEN",
        formula_version="1.0",
        category=inputs.get("category", "Generic"),
        supplier=supplier,
        rfq_scenario=inputs.get("rfq_scenario"),
        input_snapshot=deepcopy(inputs),
        raw_output=preserved,
        resolutions=tuple(resolutions),
        intermediate_steps=_authoritative_steps(authoritative_result),
        weighted_contribution=deepcopy(contribution),
        recommendation_impact="Ranking contribution only; technical eligibility remains independent.",
        configuration_versions={"weight_profile": weight_profile_version},
    )


def build_recommendation_eligibility_trace(*, inputs, authoritative_result, resolutions=(), supplier=None, rule_version="1.0"):
    preserved = deepcopy(authoritative_result)
    status = authoritative_result.get("status") if isinstance(authoritative_result, dict) else None
    blocker = None
    if status == "Blocked":
        blocker = {"rule_id": "recommendation_block", "status": status, "reasons": authoritative_result.get("reasons", [])}
    return build_trace(
        calculation_id="ELG-001",
        formula_id="F-ELIGIBILITY",
        formula_version="1.0",
        category=inputs.get("category", "All"),
        supplier=supplier,
        rfq_scenario=inputs.get("rfq_scenario"),
        input_snapshot=deepcopy(inputs),
        raw_output=preserved,
        resolutions=tuple(resolutions),
        intermediate_steps=(IntermediateStep("eligibility status", status, "status", available=status is not None),),
        blocking_rule_record=blocker,
        recommendation_impact=status,
        configuration_versions={"rule": rule_version},
    )
