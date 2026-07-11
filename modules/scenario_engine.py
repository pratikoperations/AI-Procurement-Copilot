"""Scenario simulation for procurement intelligence recommendations."""

from copy import deepcopy

from modules.allocation_optimizer import optimize_allocation
from modules.decision_engine import generate_decision
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


def apply_scenario(suppliers_df, scenario_name):
    if scenario_name not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario_name}")
    settings = SCENARIOS[scenario_name]
    result = suppliers_df.copy(deep=True)
    if "price_multiplier" in settings:
        result["Quoted Unit Price USD"] = result["Quoted Unit Price USD"] * settings["price_multiplier"]
    if "lead_time_multiplier" in settings:
        result["Lead Time Days"] = result["Lead Time Days"] * settings["lead_time_multiplier"]
    if "moq_multiplier" in settings:
        result["MOQ"] = result["MOQ"] * settings["moq_multiplier"]
    if "capacity_multiplier" in settings and "Supplier Capacity" in result.columns:
        result["Supplier Capacity"] = result["Supplier Capacity"] * settings["capacity_multiplier"]
    if "esg_penalty" in settings:
        for column in ["Recyclability", "Certification", "Carbon Score", "EPR Readiness", "PCR Content %"]:
            if column in result.columns:
                result[column] = (result[column] - settings["esg_penalty"]).clip(lower=0)
    return result, settings


def run_intelligence_scenario(suppliers_df, assumptions, scenario_name):
    scenario_df, settings = apply_scenario(suppliers_df, scenario_name)
    scenario_assumptions = deepcopy(assumptions)
    scenario_assumptions["freight_shock"] = float(assumptions.get("freight_shock", 0)) + float(settings.get("freight_shock_delta", 0))
    scored = enrich_supplier_scores(scenario_df, scenario_assumptions)
    allocation = optimize_allocation(scored, scenario_assumptions["annual_volume"])
    decision = generate_decision(scored, allocation["allocation_df"])
    return {
        "scenario": scenario_name,
        "scored_df": scored,
        "allocation": allocation,
        "decision": decision,
    }
