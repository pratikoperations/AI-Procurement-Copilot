"""Scenario simulation for procurement intelligence recommendations."""

from copy import deepcopy

import pandas as pd

from modules.decision_engine import generate_decision
from modules.flexible_laminate_cost import SUPPORTED_STRUCTURES
from modules.multi_supplier_allocation_scenario import run_scenario_allocation
from modules.scoring import enrich_supplier_scores

SCENARIOS = {
    "Base Case": {},
    "Price Increase": {"price_multiplier": 1.05},
    "Lead-Time Increase": {"lead_time_multiplier": 2.0},
    "MOQ Increase": {"moq_multiplier": 1.25},
    "Capacity Reduction": {"capacity_multiplier": 0.70},
    "Currency Fluctuation": {"price_multiplier": 1.08},
    "Freight Increase": {"freight_shock_delta": 0.50},
    "ESG Penalty": {"esg_penalty": 15},
}

FLEXIBLE_LAMINATE_SCENARIOS = (
    "Base Case",
    "Polymer Index +20%",
    "MetPET Availability Stress",
    "Adhesive and Conversion Cost +15%",
    "Demand +25%",
    "Press and Lamination Capacity Stress",
    "Tooling Replacement Scenario",
)
SCENARIO_ASSUMPTION_VERSION = "C2.5-SCENARIO-v1"

POLYMER_EXPOSURE_SHARE = {
    "PET / PE": 0.72,
    "PET / MetPET / PE": 0.70,
    "BOPP / CPP": 0.74,
}
ADHESIVE_CONVERSION_EXPOSURE_SHARE = {
    "PET / PE": 0.16,
    "PET / MetPET / PE": 0.20,
    "BOPP / CPP": 0.15,
}
METPET_SHARE = 0.21
METPET_INDEX_STRESS = 0.30
CAPACITY_STRESS_DELTA = 20.0
METPET_AVAILABILITY_DELTA = 35.0


def _validate_laminate_context(suppliers_df: pd.DataFrame, assumptions: dict) -> str:
    structure = str(assumptions.get("laminate_structure", "")).strip()
    if structure not in SUPPORTED_STRUCTURES:
        raise ValueError("Flexible Laminates scenarios require an explicit supported laminate structure.")
    if "Laminate Structure" not in suppliers_df.columns:
        raise ValueError("Flexible Laminates scenario data must include Laminate Structure.")
    actual = set(suppliers_df["Laminate Structure"].astype(str).str.strip())
    if actual != {structure}:
        raise ValueError("Scenario supplier structures must match the explicit selected laminate structure.")
    return structure


def apply_flexible_laminate_scenario(
    suppliers_df: pd.DataFrame,
    assumptions: dict,
    scenario_name: str,
) -> tuple[pd.DataFrame, dict, dict]:
    """Apply one controlled C2 scenario without mutating source inputs."""
    if scenario_name not in FLEXIBLE_LAMINATE_SCENARIOS:
        raise ValueError(f"Unknown Flexible Laminates scenario: {scenario_name}")

    structure = _validate_laminate_context(suppliers_df, assumptions)
    result = suppliers_df.copy(deep=True)
    scenario_assumptions = deepcopy(assumptions)
    metadata = {
        "scenario": scenario_name,
        "structure": structure,
        "applicable": True,
        "scenario_assumption_version": SCENARIO_ASSUMPTION_VERSION,
        "assumption_basis": (
            "Synthetic controlled C2 scenario assumptions; not a market forecast "
            "or audited supplier evidence."
        ),
        "evidence_origin": "controlled_synthetic",
    }

    if scenario_name == "Polymer Index +20%":
        exposure = POLYMER_EXPOSURE_SHARE[structure]
        result["Quoted Unit Price USD"] *= 1 + 0.20 * exposure
        metadata.update({"polymer_index_change": 0.20, "polymer_exposure_share": exposure})

    elif scenario_name == "MetPET Availability Stress":
        if structure != "PET / MetPET / PE":
            metadata.update({
                "applicable": False,
                "reason": "MetPET stress applies only to PET / MetPET / PE.",
            })
        else:
            result["Quoted Unit Price USD"] *= 1 + METPET_SHARE * METPET_INDEX_STRESS
            result["Substrate Availability %"] = (
                result["Substrate Availability %"] - METPET_AVAILABILITY_DELTA
            ).clip(lower=0)
            metadata.update({
                "metpet_share": METPET_SHARE,
                "metpet_index_stress": METPET_INDEX_STRESS,
                "substrate_availability_delta": -METPET_AVAILABILITY_DELTA,
            })

    elif scenario_name == "Adhesive and Conversion Cost +15%":
        exposure = ADHESIVE_CONVERSION_EXPOSURE_SHARE[structure]
        result["Quoted Unit Price USD"] *= 1 + 0.15 * exposure
        metadata.update({
            "adhesive_conversion_change": 0.15,
            "adhesive_conversion_exposure_share": exposure,
        })

    elif scenario_name == "Demand +25%":
        scenario_assumptions["demand_change"] = 0.25
        metadata["demand_change"] = 0.25

    elif scenario_name == "Press and Lamination Capacity Stress":
        result["Press Capacity Utilisation %"] = (
            result["Press Capacity Utilisation %"] + CAPACITY_STRESS_DELTA
        ).clip(upper=100)
        result["Lamination Capacity Utilisation %"] = (
            result["Lamination Capacity Utilisation %"] + CAPACITY_STRESS_DELTA
        ).clip(upper=100)
        metadata["capacity_utilisation_delta"] = CAPACITY_STRESS_DELTA

    elif scenario_name == "Tooling Replacement Scenario":
        printed = result["Print Profile"].astype(str) != "Unprinted"
        existing_confirmed = (
            printed
            & result["Tooling Status"].astype(str).eq("Existing")
            & result["Existing Tooling Available"].astype(str).eq("Yes")
        )
        already_new = printed & result["Tooling Status"].astype(str).eq("New")
        not_applicable = ~printed
        existing_unconfirmed = (
            printed
            & result["Tooling Status"].astype(str).eq("Existing")
            & ~result["Existing Tooling Available"].astype(str).eq("Yes")
        )
        if existing_unconfirmed.any():
            raise ValueError(
                "Tooling Replacement Scenario requires Existing Tooling Available = Yes "
                "for every Existing printed-tooling row."
            )

        if existing_confirmed.any():
            amortisation = (
                result.loc[existing_confirmed, "Number of Colours"].astype(float)
                * result.loc[existing_confirmed, "Tooling Cost per Colour USD"].astype(float)
                / result.loc[existing_confirmed, "Tooling Lifetime Volume kg"].astype(float)
            )
            result.loc[existing_confirmed, "Quoted Unit Price USD"] += amortisation
            result.loc[existing_confirmed, "Tooling Status"] = "New"
            result.loc[existing_confirmed, "Existing Tooling Available"] = "Not applicable"
            result.loc[existing_confirmed, "Tooling Availability"] = "Not applicable"

        metadata.update({
            "replacement_applied_count": int(existing_confirmed.sum()),
            "already_new_tooling_count": int(already_new.sum()),
            "not_applicable_count": int(not_applicable.sum()),
            "tooling_replacement_basis": (
                "Replacement economics apply only to printed rows with confirmed reusable "
                "existing tooling. No physical damage, loss, or unavailability is asserted."
            ),
        })

    return result, scenario_assumptions, metadata


def _no_winner_decision(scenario_name: str) -> dict:
    return {
        "scenario": scenario_name,
        "recommended_supplier": "No technically eligible supplier",
        "recommendation": "No technically eligible supplier",
        "award_confidence": 0.0,
        "confidence_governance": "No award confidence because no supplier is technically eligible.",
        "governance": "No fallback award is permitted. Human technical review is mandatory.",
    }


def _blocked_route_decision(scenario_name: str, scenario_allocation) -> dict:
    route = scenario_allocation.route_result
    reasons = "; ".join(route.blocking_reasons) if route is not None else "Scenario is not applicable."
    return {
        "scenario": scenario_name,
        "recommended_supplier": "No canonical allocation available",
        "recommendation": "No canonical allocation available",
        "award_confidence": 0.0,
        "confidence_governance": reasons,
        "governance": (
            "Canonical scenario allocation is blocked. No legacy fallback or supplier award is permitted; "
            "human procurement review is mandatory."
        ),
    }


def _ineligibility_reasons(scored: pd.DataFrame) -> str:
    reasons = []
    if "technical_ineligibility_reasons" in scored.columns:
        for value in scored.loc[~scored["technical_eligible"].astype(bool), "technical_ineligibility_reasons"]:
            if isinstance(value, (list, tuple, set)):
                reasons.extend(str(item) for item in value if str(item).strip())
            elif str(value).strip() and str(value).strip().lower() != "nan":
                reasons.extend(part.strip() for part in str(value).split(";") if part.strip())
    return "; ".join(dict.fromkeys(reasons)) or "Technical eligibility thresholds were not met."


def run_flexible_laminate_scenario(
    suppliers_df: pd.DataFrame,
    assumptions: dict,
    scenario_name: str,
) -> dict:
    """Run one C2 scenario through scoring and the canonical allocation route."""
    scenario_df, scenario_assumptions, metadata = apply_flexible_laminate_scenario(
        suppliers_df,
        assumptions,
        scenario_name,
    )
    scored = enrich_supplier_scores(scenario_df, scenario_assumptions)
    eligible = scored[scored["technical_eligible"].astype(bool)].copy()
    annual_volume = float(scenario_assumptions["annual_volume"]) * (
        1 + float(scenario_assumptions.get("demand_change", 0.0))
    )
    scenario_allocation = run_scenario_allocation(
        scored,
        scenario_assumptions,
        scenario_name=scenario_name,
        effective_annual_volume=annual_volume,
        scenario_applicable=bool(metadata["applicable"]),
        scenario_assumption_version=metadata["scenario_assumption_version"],
        scenario_metadata=metadata,
        evidence_origin=metadata.get("evidence_origin"),
    )
    canonical_allocation = scenario_allocation.allocation_df.copy(deep=True)
    compatibility_allocation = scenario_allocation.compatibility_allocation()

    if not metadata["applicable"]:
        decision = {
            "scenario": scenario_name,
            "recommended_supplier": "Not applicable",
            "recommendation": "Not applicable",
            "award_confidence": None,
            "confidence_governance": metadata.get("reason", "Scenario is not applicable."),
        }
        winner = None
    elif eligible.empty:
        decision = _no_winner_decision(scenario_name)
        winner = None
    elif not scenario_allocation.allocation_available:
        decision = _blocked_route_decision(scenario_name, scenario_allocation)
        winner = None
    else:
        decision = generate_decision(eligible, canonical_allocation)
        if len(eligible) == 1:
            decision["award_confidence"] = min(float(decision.get("award_confidence", 60.0)), 60.0)
            decision["confidence_governance"] = (
                "Single technically eligible supplier — competition confidence constrained."
            )
        else:
            decision["confidence_governance"] = (
                "Award confidence calculated from technically eligible suppliers only."
            )
        winner = eligible.iloc[0]

    return {
        "scenario": scenario_name,
        "metadata": metadata,
        "assumptions": scenario_assumptions,
        "scenario_df": scenario_df,
        "scored_df": scored,
        "eligible_df": eligible,
        "winner": winner,
        "scenario_allocation": scenario_allocation,
        "canonical_allocation_df": canonical_allocation,
        "standard_allocation_df": canonical_allocation.copy(deep=True),
        "optimized_allocation": compatibility_allocation,
        "decision": decision,
        "effective_annual_volume": annual_volume,
        "ineligibility_reasons": _ineligibility_reasons(scored) if eligible.empty else "",
    }


def run_all_flexible_laminate_scenarios(suppliers_df: pd.DataFrame, assumptions: dict) -> list[dict]:
    """Run the complete governed seven-scenario C2 set in deterministic order."""
    return [
        run_flexible_laminate_scenario(suppliers_df, assumptions, scenario)
        for scenario in FLEXIBLE_LAMINATE_SCENARIOS
    ]


def apply_scenario(suppliers_df, scenario_name):
    if scenario_name not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario_name}")
    settings = SCENARIOS[scenario_name]
    result = suppliers_df.copy(deep=True)
    if "price_multiplier" in settings:
        result["Quoted Unit Price USD"] *= settings["price_multiplier"]
    if "lead_time_multiplier" in settings:
        result["Lead Time Days"] *= settings["lead_time_multiplier"]
    if "moq_multiplier" in settings:
        result["MOQ"] *= settings["moq_multiplier"]
    if "capacity_multiplier" in settings and "Supplier Capacity" in result.columns:
        result["Supplier Capacity"] *= settings["capacity_multiplier"]
    if "esg_penalty" in settings:
        for column in ["Recyclability", "Certification", "Carbon Score", "EPR Readiness", "PCR Content %"]:
            if column in result.columns:
                result[column] = (result[column] - settings["esg_penalty"]).clip(lower=0)
    return result, settings


def run_intelligence_scenario(suppliers_df, assumptions, scenario_name):
    if (
        assumptions.get("category") == "Packaging Procurement"
        and assumptions.get("commodity") == "Flexible Laminates"
        and scenario_name in FLEXIBLE_LAMINATE_SCENARIOS
    ):
        return run_flexible_laminate_scenario(suppliers_df, assumptions, scenario_name)

    scenario_df, settings = apply_scenario(suppliers_df, scenario_name)
    scenario_assumptions = deepcopy(assumptions)
    scenario_assumptions["freight_shock"] = float(assumptions.get("freight_shock", 0)) + float(
        settings.get("freight_shock_delta", 0)
    )
    scored = enrich_supplier_scores(scenario_df, scenario_assumptions)
    annual_volume = float(scenario_assumptions["annual_volume"]) * (
        1 + float(scenario_assumptions.get("demand_change", 0.0))
    )
    scenario_allocation = run_scenario_allocation(
        scored,
        scenario_assumptions,
        scenario_name=scenario_name,
        effective_annual_volume=annual_volume,
        scenario_applicable=True,
        scenario_assumption_version="GENERIC-SCENARIO-v1",
        scenario_metadata={
            "scenario": scenario_name,
            "settings": dict(settings),
            "evidence_origin": "controlled_synthetic",
        },
        evidence_origin="controlled_synthetic",
    )
    eligible = (
        scored[scored["technical_eligible"].astype(bool)].copy()
        if "technical_eligible" in scored.columns
        else scored.copy()
    )
    if scenario_allocation.allocation_available and not eligible.empty:
        decision = generate_decision(eligible, scenario_allocation.allocation_df)
    elif eligible.empty:
        decision = _no_winner_decision(scenario_name)
    else:
        decision = _blocked_route_decision(scenario_name, scenario_allocation)
    return {
        "scenario": scenario_name,
        "scored_df": scored,
        "scenario_allocation": scenario_allocation,
        "allocation": scenario_allocation.compatibility_allocation(),
        "decision": decision,
    }
