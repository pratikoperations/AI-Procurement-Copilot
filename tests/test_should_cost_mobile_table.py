"""Contract tests for the mobile-safe should-cost component table."""

from pathlib import Path

import pandas as pd
import pandas.testing as pdt
import pytest

from modules.dashboard import (
    build_should_cost_column_config,
    build_should_cost_display,
)


@pytest.fixture
def should_cost_source():
    return pd.DataFrame(
        {
            "Component": ["Substrate / Paper", "Conversion", "Freight Buffer"],
            "Unit Cost USD": [0.3000, 0.0800, 0.0500],
        }
    )


@pytest.mark.parametrize(
    ("currency", "expected_columns"),
    [
        ("USD", ["Component", "Unit Cost (USD)"]),
        ("INR", ["Component", "Unit Cost (INR)"]),
        ("Both", ["Component", "Unit Cost (USD)", "Unit Cost (INR)"]),
    ],
)
def test_should_cost_display_preserves_component_and_governed_currency_columns(
    should_cost_source,
    currency,
    expected_columns,
):
    display = build_should_cost_display(
        should_cost_source,
        {"display_currency": currency, "fx_rate": 83},
    )

    assert list(display.columns) == expected_columns
    assert display["Component"].tolist() == should_cost_source["Component"].tolist()


def test_should_cost_display_does_not_mutate_authoritative_source(should_cost_source):
    original = should_cost_source.copy(deep=True)

    build_should_cost_display(
        should_cost_source,
        {"display_currency": "Both", "fx_rate": 83},
    )

    pdt.assert_frame_equal(should_cost_source, original)


def test_should_cost_display_preserves_authoritative_values(should_cost_source):
    display = build_should_cost_display(
        should_cost_source,
        {"display_currency": "Both", "fx_rate": 83},
    )

    assert display["Unit Cost (USD)"].tolist() == pytest.approx(
        should_cost_source["Unit Cost USD"].tolist()
    )
    assert display["Unit Cost (INR)"].tolist() == pytest.approx(
        (should_cost_source["Unit Cost USD"] * 83).tolist()
    )
    assert display["Unit Cost (USD)"].sum() == pytest.approx(
        should_cost_source["Unit Cost USD"].sum()
    )


@pytest.mark.parametrize("currency", ["USD", "INR", "Both"])
def test_renderer_config_covers_every_displayed_column(should_cost_source, currency):
    display = build_should_cost_display(
        should_cost_source,
        {"display_currency": currency, "fx_rate": 83},
    )
    config = build_should_cost_column_config(display)

    assert list(config) == list(display.columns)
    assert "Component" in config
    assert any(column.startswith("Unit Cost (") for column in config)


def test_should_cost_renderer_uses_explicit_order_and_column_configuration():
    source = Path("modules/dashboard.py").read_text(encoding="utf-8")
    function = source.split("def render_should_cost_section", 1)[1].split(
        "def render_tco_breakdown", 1
    )[0]

    assert "build_should_cost_display(should_cost_df, assumptions)" in function
    assert "column_order=list(display.columns)" in function
    assert "column_config=build_should_cost_column_config(display)" in function
    assert "chart_df = should_cost_df.copy()" in function
    assert 'chart_df["Unit Cost USD"]' in function


def test_unrelated_dataframe_renderers_are_not_reconfigured():
    source = Path("modules/dashboard.py").read_text(encoding="utf-8")

    supplier = source.split("def render_supplier_snapshot", 1)[1].split(
        "def render_should_cost_section", 1
    )[0]
    tco = source.split("def render_tco_breakdown", 1)[1].split(
        "def render_executive_value", 1
    )[0]
    allocation = source.split("def render_allocation", 1)[1].split(
        "def render_scenario_table", 1
    )[0]

    assert "column_config=" not in supplier
    assert "column_config=" not in tco
    assert "column_config=" not in allocation
