from pathlib import Path

import pytest

from modules.flexible_laminate_cost import calculate_flexible_laminate_should_cost
from modules.sidebar import (
    LAMINATE_COLOUR_COUNT_KEY,
    LAMINATE_PRINT_PROFILE_KEY,
    LAMINATE_TOOLING_AVAILABILITY_KEY,
    LAMINATE_TOOLING_COST_KEY,
    LAMINATE_TOOLING_LIFETIME_KEY,
    LAMINATE_TOOLING_STATUS_KEY,
    normalize_laminate_colour_count,
    normalize_laminate_tooling_state,
)


def test_default_flexible_laminate_profile_uses_four_colours():
    assert normalize_laminate_colour_count("Up to 4 colours", 4) == 4
    result = calculate_flexible_laminate_should_cost(
        print_profile="Up to 4 colours",
        number_of_colours=4,
    )
    assert result["target_unit_cost_usd"] > 0


def test_five_to_eight_profile_accepts_five_colours():
    assert normalize_laminate_colour_count("5–8 colours", 5) == 5
    result = calculate_flexible_laminate_should_cost(
        print_profile="5–8 colours",
        number_of_colours=5,
    )
    assert result["target_unit_cost_usd"] > 0


def test_switching_to_up_to_four_normalizes_stale_five_to_eight_value():
    assert normalize_laminate_colour_count("Up to 4 colours", 8) == 4


def test_switching_to_five_to_eight_normalizes_stale_up_to_four_value():
    assert normalize_laminate_colour_count("5–8 colours", 4) == 5


def test_switching_to_unprinted_normalizes_colour_count_to_zero():
    assert normalize_laminate_colour_count("Unprinted", 4) == 0


def test_switching_to_unprinted_normalizes_all_tooling_state():
    state = normalize_laminate_tooling_state(
        "Unprinted",
        "New",
        "Not applicable",
        250.0,
        250000.0,
    )
    assert state == {
        "tooling_status": "Not applicable",
        "existing_tooling_available": "Not applicable",
        "tooling_cost_per_colour_usd": 0.0,
        "tooling_lifetime_volume_kg": 0.0,
    }


@pytest.mark.parametrize("profile", ["Up to 4 colours", "5–8 colours"])
def test_switching_from_unprinted_restores_governed_printed_tooling_defaults(profile):
    state = normalize_laminate_tooling_state(
        profile,
        "Not applicable",
        "Not applicable",
        0.0,
        0.0,
    )
    assert state == {
        "tooling_status": "New",
        "existing_tooling_available": "Not applicable",
        "tooling_cost_per_colour_usd": 250.0,
        "tooling_lifetime_volume_kg": 250000.0,
    }


def test_valid_unprinted_direct_engine_call_returns_zero_tooling_amortisation():
    result = calculate_flexible_laminate_should_cost(
        print_profile="Unprinted",
        number_of_colours=0,
        tooling_status="Not applicable",
        existing_tooling_available="Not applicable",
        tooling_cost_per_colour_usd=0.0,
        tooling_lifetime_volume_kg=0.0,
    )
    assert result["components"]["Print Tooling Amortisation"] == 0.0
    assert result["components"]["Printing Ink Process Allowance"] == 0.0
    assert result["components"]["Printing Conversion"] == 0.0


@pytest.mark.parametrize(
    "profile,colours",
    [("Unprinted", 1), ("Up to 4 colours", 5), ("5–8 colours", 4)],
)
def test_direct_invalid_engine_colour_combinations_remain_fail_closed(profile, colours):
    with pytest.raises(ValueError, match="inconsistent"):
        calculate_flexible_laminate_should_cost(
            print_profile=profile,
            number_of_colours=colours,
        )


@pytest.mark.parametrize(
    "tooling_status,availability,cost,error",
    [
        ("New", "Not applicable", 0.0, "Not applicable tooling status"),
        ("Not applicable", "Yes", 0.0, "Not applicable tooling status and availability"),
        ("Not applicable", "Not applicable", 250.0, "zero tooling cost"),
    ],
)
def test_invalid_unprinted_tooling_contracts_remain_fail_closed(
    tooling_status,
    availability,
    cost,
    error,
):
    with pytest.raises(ValueError, match=error):
        calculate_flexible_laminate_should_cost(
            print_profile="Unprinted",
            number_of_colours=0,
            tooling_status=tooling_status,
            existing_tooling_available=availability,
            tooling_cost_per_colour_usd=cost,
            tooling_lifetime_volume_kg=0.0,
        )


def test_sidebar_uses_explicit_stable_widget_keys_and_normalization():
    source = Path("modules/sidebar.py").read_text(encoding="utf-8")
    for key in (
        LAMINATE_PRINT_PROFILE_KEY,
        LAMINATE_COLOUR_COUNT_KEY,
        LAMINATE_TOOLING_STATUS_KEY,
        LAMINATE_TOOLING_AVAILABILITY_KEY,
        LAMINATE_TOOLING_COST_KEY,
        LAMINATE_TOOLING_LIFETIME_KEY,
    ):
        assert key in source
    assert "normalize_laminate_colour_count" in source
    assert "normalize_laminate_tooling_state" in source
    assert "disabled=laminate_print_profile == \"Unprinted\"" in source
    assert "disabled=unprinted" in source
