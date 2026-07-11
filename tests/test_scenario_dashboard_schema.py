import pandas as pd
import pytest

from modules.dashboard import (
    SCENARIO_ANNUAL_TCO_CANDIDATES,
    SCENARIO_SUPPLIER_CANDIDATES,
    resolve_scenario_column,
)
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
        "display_currency": "USD",
        "fx_rate": 83.0,
        "category_profile": {"unit": unit},
    }


def test_dashboard_resolves_governed_scenario_schema():
    scenario_df = run_scenario_table(
        get_demo_data("Raw Material Procurement", "PET Resin"),
        _assumptions("Raw Material Procurement", "PET Resin", "kg"),
    )
    assert resolve_scenario_column(
        scenario_df.columns,
        SCENARIO_ANNUAL_TCO_CANDIDATES,
        "annual TCO column",
    ) == "Annual TCO (USD)"
    assert resolve_scenario_column(
        scenario_df.columns,
        SCENARIO_SUPPLIER_CANDIDATES,
        "supplier column",
    ) == "Winning Supplier"


def test_dashboard_retains_backward_compatibility_for_legacy_schema():
    legacy_columns = pd.Index(["Scenario", "Winning Supplier", "Annual TCO USD"])
    assert resolve_scenario_column(
        legacy_columns,
        SCENARIO_ANNUAL_TCO_CANDIDATES,
        "annual TCO column",
    ) == "Annual TCO USD"


def test_dashboard_raises_clear_error_for_invalid_schema():
    with pytest.raises(KeyError, match="missing required annual TCO column"):
        resolve_scenario_column(
            pd.Index(["Scenario", "Winning Supplier"]),
            SCENARIO_ANNUAL_TCO_CANDIDATES,
            "annual TCO column",
        )


def test_packaging_and_raw_material_scenarios_share_renderer_contract():
    packaging = run_scenario_table(
        get_demo_data("Packaging Procurement", "Corrugated Board"),
        _assumptions("Packaging Procurement", "Corrugated Board", "piece"),
    )
    raw_material = run_scenario_table(
        get_demo_data("Raw Material Procurement", "PET Resin"),
        _assumptions("Raw Material Procurement", "PET Resin", "kg"),
    )
    for frame in (packaging, raw_material):
        assert "Annual TCO (USD)" in frame.columns
        assert "Risk Resilience Score" in frame.columns
        assert "Winning Supplier" in frame.columns
        assert set(frame["Scenario"]) >= {
            "Base Case",
            "Freight +50%",
            "Demand -25%",
            "Combined Stress",
        }
