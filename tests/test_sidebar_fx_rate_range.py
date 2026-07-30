"""Deterministic contract tests for the USD-INR sidebar control."""

from modules.config import DEFAULT_FX_RATE
from modules.sidebar import (
    FX_RATE_MAX,
    FX_RATE_MIN,
    FX_RATE_STEP,
    build_sidebar_result,
)


def test_fx_rate_slider_contract_constants() -> None:
    assert FX_RATE_MIN == 60
    assert FX_RATE_MAX == 150
    assert FX_RATE_STEP == 1
    assert FX_RATE_MIN <= DEFAULT_FX_RATE <= FX_RATE_MAX


def test_sidebar_result_preserves_fx_rate() -> None:
    result = build_sidebar_result(
        category_profile={"unit": "kg"},
        fx_rate=97,
    )

    assert result["fx_rate"] == 97
    assert result["annual_volume_unit"] == "kg"
