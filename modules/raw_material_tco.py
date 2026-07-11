"""Risk-adjusted TCO engine for raw-material procurement."""

from modules.raw_material_risk import calculate_raw_material_risk
from modules.risk import get_advance_percent, get_payment_days, normalize_incoterm
from modules.tco import freight_cost_factor_for_scenario
from modules.utils import extract_number


def calculate_raw_material_tco(
    row,
    annual_volume,
    commodity_shock=0.0,
    freight_shock=0.0,
    demand_change=0.0,
    cost_of_capital=0.12,
    inventory_carrying_rate=0.18,
):
    """Calculate delivered, working-capital, and risk-adjusted raw-material TCO."""
    base_price = float(row.get("Quoted Unit Price USD", 0.0))
    effective_volume = max(float(annual_volume) * (1 + demand_change), 1.0)
    scenario_price = base_price * (1 + commodity_shock)

    incoterm = normalize_incoterm(row.get("Incoterms", "DDP"))
    freight_factor = freight_cost_factor_for_scenario(
        incoterm,
        freight_shock,
        max_freight_exposure=0.08,
        embedded_freight_share=float(row.get("Embedded Freight Share", 0.02)),
    )
    freight_cost = scenario_price * freight_factor
    duty_rate = float(row.get("Duty %", 0)) / 100
    duty_cost = scenario_price * duty_rate

    moq = max(extract_number(row.get("MOQ", 1000), 1000), 1.0)
    lead_days = max(extract_number(row.get("Lead Time Days", 30), 30), 1.0)
    payment_days = get_payment_days(row.get("Payment Terms", "Net 30"))
    advance = get_advance_percent(row.get("Payment Terms", "Net 30"))

    cycle_stock = moq / 2
    safety_stock = effective_volume * (lead_days / 365) * 0.5
    inventory_cost = ((cycle_stock + safety_stock) * scenario_price * inventory_carrying_rate) / effective_volume
    advance_cost = scenario_price * advance * cost_of_capital * 60 / 365
    credit_benefit = scenario_price * (1 - advance) * cost_of_capital * payment_days / 365
    working_capital = advance_cost - credit_benefit

    risk = calculate_raw_material_risk(row)
    failure_probability = (100 - risk["risk_score"]) / 100 * 0.25
    risk_penalty = scenario_price * failure_probability * 0.65
    volatility_buffer = scenario_price * float(row.get("Commodity Volatility %", 15)) / 100 * 0.10

    adjusted = scenario_price + freight_cost + duty_cost + inventory_cost + working_capital + risk_penalty + volatility_buffer
    return {
        "scenario_unit_price_usd": round(scenario_price, 4),
        "freight_cost_usd": round(freight_cost, 4),
        "duty_cost_usd": round(duty_cost, 4),
        "inventory_cost_usd": round(inventory_cost, 4),
        "working_capital_impact_usd": round(working_capital, 4),
        "risk_penalty_usd": round(risk_penalty, 4),
        "volatility_buffer_usd": round(volatility_buffer, 4),
        "lead_time_buffer_usd": 0.0,
        "adjusted_tco_unit_usd": round(adjusted, 4),
        "annual_tco_usd": round(adjusted * effective_volume, 2),
        "failure_probability": round(failure_probability, 4),
        **risk,
    }
