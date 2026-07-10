"""Negotiation simulator and playbook generator."""


def simulate_negotiation(
    supplier,
    annual_volume,
    price_reduction=0.03,
    freight_improvement=0.20,
    payment_extension_days=30,
    risk_reduction=0.15,
    cost_of_capital=0.12,
):
    """Simulate annual TCO savings from commercial negotiation levers."""
    current_tco = float(supplier["adjusted_tco_unit_usd"])
    simulated_price = float(supplier["scenario_unit_price_usd"]) * (1 - price_reduction)
    simulated_freight = float(supplier["freight_cost_usd"]) * (1 - freight_improvement)
    payment_benefit = simulated_price * cost_of_capital * payment_extension_days / 365
    simulated_risk = float(supplier["risk_penalty_usd"]) * (1 - risk_reduction)

    simulated_tco = (
        simulated_price
        + simulated_freight
        + float(supplier["inventory_cost_usd"])
        + float(supplier["working_capital_impact_usd"])
        - payment_benefit
        + float(supplier["lead_time_buffer_usd"])
        + simulated_risk
    )
    annual_saving = max(current_tco - simulated_tco, 0) * annual_volume

    return {
        "current_tco_unit_usd": round(current_tco, 4),
        "simulated_tco_unit_usd": round(simulated_tco, 4),
        "annual_saving_usd": round(annual_saving, 2),
    }


def generate_negotiation_playbook(supplier, should_cost_target, lowest_supplier_name, lowest_price, annual_saving):
    """Generate a structured negotiation playbook."""
    target_price = max(float(should_cost_target) + 0.02, float(supplier["Quoted Unit Price USD"]) * 0.94)
    walkaway_price = min(float(supplier["Quoted Unit Price USD"]), float(should_cost_target) + 0.06)

    return f"""
Negotiation Objective:
Move {supplier['Supplier']} from the current quoted price of ${supplier['Quoted Unit Price USD']:.4f}
toward a target price of ${target_price:.4f} while protecting service, quality, compliance, ESG, and delivery commitments.

BATNA:
Lowest quoted supplier is {lowest_supplier_name} at ${lowest_price:.4f}.
However, the award decision must reflect TCO, risk, working capital, service, and performance — not price alone.

Target Price:
${target_price:.4f}

Walk-Away Price:
${walkaway_price:.4f}

Give / Get Matrix:
- Give: Volume commitment → Get: Unit price reduction
- Give: Longer contract visibility → Get: Index-linked pricing formula
- Give: Forecast sharing → Get: MOQ flexibility
- Give: Preferred supplier status → Get: OTIF SLA and capacity reservation
- Give: Faster approvals → Get: Tooling / artwork cost transparency

Estimated Annual TCO Saving:
${annual_saving:,.0f}
""".strip()
