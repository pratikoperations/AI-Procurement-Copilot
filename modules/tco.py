"""Advanced TCO engine for packaging procurement."""

from modules.risk import calculate_risk, get_advance_percent, get_payment_days, normalize_incoterm
from modules.utils import extract_number


def freight_factor_for_incoterm(incoterm, max_freight_exposure=0.06):
    factors = {
        "DDP": 0.00,
        "DAP": max_freight_exposure * 0.20,
        "CIF": max_freight_exposure * 0.35,
        "FOB": max_freight_exposure * 0.75,
        "EXW": max_freight_exposure,
        "UNKNOWN": max_freight_exposure * 0.60,
    }
    return factors.get(incoterm, max_freight_exposure * 0.60)


def freight_cost_factor_for_scenario(
    incoterm,
    freight_shock,
    max_freight_exposure=0.06,
    embedded_freight_share=0.02,
):
    """Return scenario freight factor, including pass-through exposure for delivered quotes.

    DDP prices already include baseline freight, so base-case incremental freight remains zero.
    During an explicit freight shock, a transparent embedded freight share is stressed to
    represent supplier pass-through rather than treating delivered pricing as risk-free.
    """
    direct_factor = freight_factor_for_incoterm(incoterm, max_freight_exposure)
    shock = max(float(freight_shock or 0.0), 0.0)
    if direct_factor == 0:
        return embedded_freight_share * shock
    return direct_factor * (1 + shock)


def calculate_supplier_tco(
    row,
    annual_volume,
    raw_material_shock=0.0,
    freight_shock=0.0,
    demand_change=0.0,
    cost_of_capital=0.12,
    inventory_carrying_rate=0.18,
    max_freight_exposure=0.06,
    max_failure_probability=0.20,
    business_impact_multiplier=0.50,
):
    """Calculate risk-adjusted TCO per supplier."""
    base_price = float(row.get("Quoted Unit Price USD", 0.0))
    effective_volume = max(float(annual_volume) * (1 + demand_change), 1.0)
    raw_ratio = 0.60
    scenario_price = base_price * (raw_ratio * (1 + raw_material_shock) + (1 - raw_ratio))

    incoterm = normalize_incoterm(row.get("Incoterms", "DDP"))
    freight_factor = freight_cost_factor_for_scenario(
        incoterm,
        freight_shock,
        max_freight_exposure=max_freight_exposure,
        embedded_freight_share=float(row.get("Embedded Freight Share", 0.02)),
    )
    freight_cost = scenario_price * freight_factor

    moq = max(extract_number(row.get("MOQ", 10000), 10000), 1.0)
    lead_days = max(extract_number(row.get("Lead Time Days", 30), 30), 1.0)
    payment_days = get_payment_days(row.get("Payment Terms", "Net 30"))
    advance_percent = get_advance_percent(row.get("Payment Terms", "Net 30"))

    cycle_stock_units = moq / 2.0
    safety_stock_units = effective_volume * ((lead_days * 0.5) / 365.0)
    average_inventory_units = cycle_stock_units + safety_stock_units
    inventory_cost = (average_inventory_units * scenario_price * inventory_carrying_rate) / effective_volume

    advance_cost = scenario_price * advance_percent * cost_of_capital * 60 / 365
    credit_benefit = scenario_price * (1 - advance_percent) * cost_of_capital * payment_days / 365
    working_capital_impact = advance_cost - credit_benefit

    risk = calculate_risk(row)
    failure_probability = ((100 - risk["risk_score"]) / 100.0) * max_failure_probability
    risk_penalty = scenario_price * failure_probability * business_impact_multiplier

    lead_time_buffer = scenario_price * 0.015 if lead_days > 45 else scenario_price * 0.0075 if lead_days > 30 else scenario_price * 0.003 if lead_days > 21 else 0

    adjusted_unit_cost = scenario_price + freight_cost + inventory_cost + working_capital_impact + risk_penalty + lead_time_buffer
    annual_tco = adjusted_unit_cost * effective_volume

    return {
        "scenario_unit_price_usd": round(scenario_price, 4),
        "freight_cost_usd": round(freight_cost, 4),
        "inventory_cost_usd": round(inventory_cost, 4),
        "working_capital_impact_usd": round(working_capital_impact, 4),
        "risk_penalty_usd": round(risk_penalty, 4),
        "lead_time_buffer_usd": round(lead_time_buffer, 4),
        "adjusted_tco_unit_usd": round(adjusted_unit_cost, 4),
        "annual_tco_usd": round(annual_tco, 2),
        "failure_probability": round(failure_probability, 4),
        **risk,
    }
