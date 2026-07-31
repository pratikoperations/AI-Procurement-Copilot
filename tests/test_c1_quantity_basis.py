"""Focused assurance for C1 quantity-basis display governance."""

from modules.unit_display import quantity_basis_caption


def test_one_thousand_kg_equals_one_metric_tonne():
    assert quantity_basis_caption(1000, "kg") == (
        "Canonical quantity basis: 1,000 kg (1 metric tonnes)"
    )


def test_five_hundred_thousand_kg_equals_five_hundred_metric_tonnes():
    assert quantity_basis_caption(500000, "kg") == (
        "Canonical quantity basis: 500,000 kg (500 metric tonnes)"
    )


def test_packaging_pieces_remain_pieces_without_tonne_equivalence():
    assert quantity_basis_caption(500000, "piece") == (
        "Canonical quantity basis: 500,000 pieces"
    )


def test_non_kg_units_do_not_receive_tonne_equivalence():
    assert quantity_basis_caption(2500, "litre") == (
        "Canonical quantity basis: 2,500 litre"
    )


def test_fractional_metric_tonnes_use_trimmed_precision():
    assert quantity_basis_caption(1250, "kg") == (
        "Canonical quantity basis: 1,250 kg (1.25 metric tonnes)"
    )
