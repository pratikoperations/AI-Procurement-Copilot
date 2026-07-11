"""Negotiation simulator and category-aware playbook generator."""


def simulate_negotiation(
    supplier,
    annual_volume,
    price_reduction=0.03,
    freight_improvement=0.20,
    payment_extension_days=30,
    risk_reduction=0.15,
    cost_of_capital=0.12,
):
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


def generate_negotiation_playbook(
    supplier,
    should_cost_target,
    lowest_supplier_name,
    lowest_price,
    annual_saving,
    category="Packaging Procurement",
    commodity="Category",
    unit="piece",
):
    """Generate a category-aware negotiation brief."""
    target_price = max(float(should_cost_target) + 0.02, float(supplier["Quoted Unit Price USD"]) * 0.94)
    ceiling_price = min(float(supplier["Quoted Unit Price USD"]), float(should_cost_target) + 0.06)

    if category == "Raw Material Procurement":
        discussion_points = [
            "Commodity index reference and reset frequency",
            "Producer or conversion premium",
            "Grade, quality specification, and certificate of analysis",
            "Freight, duty, FX basis, and landed-cost assumptions",
            "Capacity allocation, supply assurance, and contingency supply",
            "Payment terms and lead-time protection",
        ]
        control_note = f"Protect {commodity} grade, quality, compliance, supply allocation, and delivery commitments."
    else:
        discussion_points = [
            "Material specification, conversion, printing, and tooling assumptions",
            "Scrap, freight, overhead, and margin transparency",
            "MOQ flexibility and volume-linked pricing",
            "Payment terms, lead time, and service commitments",
            "Recyclability, PCR, EPR, and quality documentation",
        ]
        control_note = "Protect material specification, print quality, compliance, ESG, and delivery commitments."

    points = "\n".join(f"- {item}" for item in discussion_points)
    return f"""NEGOTIATION OBJECTIVE
Move {supplier['Supplier']} from the normalized quoted price of ${supplier['Quoted Unit Price USD']:.4f} per {unit} toward ${target_price:.4f} per {unit}. {control_note}

COMPARATIVE POSITION
The lowest normalized quoted supplier is {lowest_supplier_name} at ${lowest_price:.4f} per {unit}. The final decision must still reflect TCO, risk resilience, working capital, service, and performance.

TARGET PRICE
${target_price:.4f} per {unit}

COMMERCIAL CEILING
${ceiling_price:.4f} per {unit}

DISCUSSION POINTS
{points}

ESTIMATED ANNUAL TCO SAVING
${annual_saving:,.0f}
""".strip()


def govern_negotiation_brief(playbook_text: str, eligibility: dict) -> str:
    """Align negotiation language with recommendation eligibility."""
    status = eligibility.get("status", "Human Review Required")
    reason = eligibility.get("reason", "Validation review remains open.")
    if status in {"Blocked", "Insufficient Data"}:
        return (
            f"NEGOTIATION BRIEF WITHHELD\n\nStatus: {status}\nReason: {reason}\n\n"
            "Commercial clarification may continue, but target and award-position language must not be used until validation issues are resolved."
        )
    if status == "Human Review Required":
        return "PROVISIONAL — HUMAN REVIEW REQUIRED\n\n" + playbook_text
    if status == "Eligible With Conditions":
        return "PROVISIONAL — CONDITIONS APPLY\n\n" + playbook_text
    return playbook_text
