from modules.data_loader import get_demo_data
from modules.scenario import run_scenario_table


def _assumptions(category, commodity, unit):
    return {
        "category": category,
        "commodity": commodity,
        "annual_volume": 500000,
        "raw_material_shock": 0.0,
        "freight_shock": 0.0,
        "demand_change": 0.0,
        "category_profile": {"unit": unit},
    }


def _scenario_rows(category, commodity, unit):
    data = get_demo_data(category, commodity)
    result = run_scenario_table(data, _assumptions(category, commodity, unit))
    return result.set_index("Scenario")


def test_raw_material_freight_shock_increases_unit_and_annual_tco():
    scenarios = _scenario_rows("Raw Material Procurement", "PET Resin", "kg")
    unit_column = "Risk-Adjusted TCO per kg (USD)"
    assert scenarios.loc["Freight +50%", unit_column] > scenarios.loc["Base Case", unit_column]
    assert scenarios.loc["Freight +50%", "Annual TCO (USD)"] > scenarios.loc["Base Case", "Annual TCO (USD)"]


def test_packaging_freight_shock_increases_unit_and_annual_tco():
    scenarios = _scenario_rows("Packaging Procurement", "Corrugated Board", "piece")
    unit_column = "Risk-Adjusted TCO per piece (USD)"
    assert scenarios.loc["Freight +50%", unit_column] > scenarios.loc["Base Case", unit_column]
    assert scenarios.loc["Freight +50%", "Annual TCO (USD)"] > scenarios.loc["Base Case", "Annual TCO (USD)"]


def test_readable_scenario_export_uses_executive_terminology():
    scenarios = _scenario_rows("Raw Material Procurement", "PET Resin", "kg")
    assert "Risk Resilience Score" in scenarios.columns
    assert "Risk Score" not in scenarios.columns
    assert "Risk-Adjusted TCO per kg (USD)" in scenarios.columns
    assert "Advanced TCO Unit USD" not in scenarios.columns
