from pathlib import Path

import pytest

from modules.flexible_laminate_cost import calculate_flexible_laminate_should_cost
from modules.sidebar import (
    LAMINATE_COLOUR_COUNT_KEY,
    LAMINATE_PRINT_PROFILE_KEY,
    normalize_laminate_colour_count,
)


def test_default_flexible_laminate_profile_uses_four_colours():
    assert normalize_laminate_colour_count("Up to 4 colours", 4) == 4
    result = calculate_flexible_laminate_should_cost(
        print_profile="Up to 4 colours",
        number_of_colours=4,
    )
    assert result["number_of_colours"] == 4


def test_five_to_eight_profile_accepts_five_colours():
    assert normalize_laminate_colour_count("5–8 colours", 5) == 5
    result = calculate_flexible_laminate_should_cost(
        print_profile="5–8 colours",
        number_of_colours=5,
    )
    assert result["number_of_colours"] == 5


def test_switching_to_up_to_four_normalizes_stale_five_to_eight_value():
    assert normalize_laminate_colour_count("Up to 4 colours", 8) == 4


def test_switching_to_five_to_eight_normalizes_stale_up_to_four_value():
    assert normalize_laminate_colour_count("5–8 colours", 4) == 5


def test_switching_to_unprinted_normalizes_colour_count_to_zero():
    assert normalize_laminate_colour_count("Unprinted", 4) == 0


@pytest.mark.parametrize(
    "profile,colours",
    [("Unprinted", 1), ("Up to 4 colours", 5), ("5–8 colours", 4)],
)
def test_direct_invalid_engine_combinations_remain_fail_closed(profile, colours):
    with pytest.raises(ValueError, match="inconsistent"):
        calculate_flexible_laminate_should_cost(
            print_profile=profile,
            number_of_colours=colours,
        )


def test_sidebar_uses_explicit_stable_widget_keys_and_normalization():
    source = Path("modules/sidebar.py").read_text(encoding="utf-8")
    assert LAMINATE_PRINT_PROFILE_KEY in source
    assert LAMINATE_COLOUR_COUNT_KEY in source
    assert "normalize_laminate_colour_count" in source
    assert "disabled=laminate_print_profile == \"Unprinted\"" in source
