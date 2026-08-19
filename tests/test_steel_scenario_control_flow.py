"""Focused regression assurance for Steel scenario participation in the shared workflow."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from modules.data_loader import get_demo_data
from modules.scenario import run_scenario_table
from modules.steel_scenario import STEEL_SCENARIOS


def _assumptions(profile: str) -> dict:
    return {
        "category": "Raw Material Procurement",
        "commodity": "Steel",
        "steel_profile": profile,
        "steel_sourcing_route": "Domestic",
        "steel_zinc_cost_usd_per_kg": 0.08 if profile != "CR_COIL_COMMERCIAL" else 0.0,
        "steel_paint_treatment_usd_per_kg": 0.12 if profile == "PPGI_COIL_Z120" else 0.0,
        "steel_import_duty_pct": 0.0,
        "steel_substitution_status": "Non-applicable",
        "annual_volume": 500000.0,
        "annual_volume_unit": "kg",
        "fx_rate": 83.0,
        "display_currency": "Both",
    }


def _steel_demo() -> pd.DataFrame:
    return get_demo_data(
        "Raw Material Procurement",
        "Steel",
        expanded_supplier_pool=True,
    )


@pytest.mark.parametrize("profile", ["CR_COIL_COMMERCIAL", "GI_COIL_Z120", "PPGI_COIL_Z120"])
def test_steel_returns_shared_scenario_table_without_terminal_ui_route(profile):
    result = run_scenario_table(_steel_demo(), _assumptions(profile))

    assert result["Scenario"].tolist() == list(STEEL_SCENARIOS)
    assert len(result) == 7
    assert result.attrs["shared_scenario_contract"] is True
    assert {
        "Winning Supplier",
        "Annual TCO (USD)",
        "Risk Resilience Score",
        "Technical Eligibility",
        "Governed Total Score",
        "Human Approval Required",
    } <= set(result.columns)
    assert result["Human Approval Required"].eq(True).all()  # noqa: E712
    assert result["Winning Supplier"].notna().all()
    assert result["Confidence"].isna().all()
    governed_scores = result.loc[result["Technical Eligibility"] == "Eligible", "Governed Total Score"]
    assert governed_scores.notna().all()


def test_steel_scenario_projection_does_not_relabel_governed_score_as_generic_confidence():
    result = run_scenario_table(_steel_demo(), _assumptions("CR_COIL_COMMERCIAL"))

    assert result["Confidence"].isna().all()
    assert result["Confidence Governance"].str.contains("governed_total_score").all()
    assert result["Confidence Governance"].str.contains("not relabelled").all()


def test_steel_scenario_engine_requires_complete_governed_volume_contract():
    assumptions = _assumptions("CR_COIL_COMMERCIAL")
    assumptions.pop("annual_volume")

    with pytest.raises(KeyError, match="annual_volume"):
        run_scenario_table(_steel_demo(), assumptions)


def test_steel_scenario_source_has_no_terminal_dashboard_dispatch():
    source = Path("modules/scenario.py").read_text(encoding="utf-8")

    assert "return _steel_scenario_table(base_df, assumptions)" in source
    assert "render_steel_governed_dashboard" not in source
    assert "Steel governed route returned without terminating" not in source
