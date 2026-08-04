"""Focused assurance for expanded synthetic supplier pools."""

import sys
from types import SimpleNamespace

from modules.data_loader import (
    get_demo_data,
    get_demo_suppliers,
    get_flexible_laminate_demo_suppliers,
    get_kraft_paper_demo_suppliers,
    get_raw_material_demo_suppliers,
    get_steel_demo_suppliers,
)


def _assert_six_distinct_suppliers(data):
    assert len(data) == 6
    assert data["Supplier"].nunique() == 6
    assert data["Quoted Unit Price USD"].nunique(dropna=False) >= 4
    assert data["Lead Time Days"].nunique() >= 4
    assert data["OTIF %"].nunique() >= 4


def _assert_three_suppliers(data):
    assert len(data) == 3
    assert data["Supplier"].nunique() == 3


def test_general_packaging_application_route_has_six_differentiated_suppliers():
    data = get_demo_data("Packaging Procurement", "Corrugated Board", expanded_supplier_pool=True)
    _assert_six_distinct_suppliers(data)
    assert set(data["Risk Category"]) >= {"Low", "Medium"}


def test_flexible_laminates_application_route_has_six_suppliers_for_every_structure():
    for structure in ("PET / PE", "PET / MetPET / PE", "BOPP / CPP"):
        data = get_demo_data(
            "Packaging Procurement",
            "Flexible Laminates",
            selected_structure=structure,
            expanded_supplier_pool=True,
        )
        _assert_six_distinct_suppliers(data)
        assert data.attrs["selected_laminate_structure"] == structure
        assert {"Conditional", "Not approved"} <= set(data["Application Approval Status"])


def test_kraft_paper_application_route_has_six_differentiated_suppliers():
    data = get_demo_data("Raw Material Procurement", "Kraft Paper", expanded_supplier_pool=True)
    _assert_six_distinct_suppliers(data)
    assert set(data["Kraft Variant"]) == {"Recycled Kraft", "Virgin Kraft"}
    assert "Conditional demonstration assumption" in set(data["Corrugated Linkage"])


def test_steel_application_route_has_six_suppliers_and_ineligible_examples():
    data = get_demo_data("Raw Material Procurement", "Steel", expanded_supplier_pool=True)
    _assert_six_distinct_suppliers(data)
    assert set(data["Currency"]) == {"USD", "INR"}
    assert "Not approved" in set(data["Application Approval"])
    assert "No" in set(data["Paint Line Capability"])
    assert data.attrs["source_label"] == "Synthetic controlled demonstration data"


def test_non_authorized_packaging_routes_remain_unexpanded_when_selector_is_true():
    for commodity in ("PET Bottles", "Labels"):
        data = get_demo_data("Packaging Procurement", commodity, expanded_supplier_pool=True)
        _assert_three_suppliers(data)


def test_non_authorized_raw_material_routes_remain_unexpanded_when_selector_is_true():
    for commodity in ("PET Resin", "Polyethylene", "Polypropylene", "Aluminium Foil", "Copper"):
        data = get_demo_data("Raw Material Procurement", commodity, expanded_supplier_pool=True)
        _assert_three_suppliers(data)


def test_explicit_false_prevents_authorized_route_expansion():
    routes = [
        ("Packaging Procurement", "Corrugated Board", None),
        ("Packaging Procurement", "Flexible Laminates", "PET / PE"),
        ("Raw Material Procurement", "Kraft Paper", None),
        ("Raw Material Procurement", "Steel", None),
    ]
    for category, commodity, structure in routes:
        data = get_demo_data(
            category,
            commodity,
            selected_structure=structure,
            expanded_supplier_pool=False,
        )
        _assert_three_suppliers(data)


def test_streamlit_runtime_default_enables_authorized_expansion(monkeypatch):
    fake_streamlit = SimpleNamespace(runtime=SimpleNamespace(exists=lambda: True))
    monkeypatch.setitem(sys.modules, "streamlit", fake_streamlit)

    data = get_demo_data("Packaging Procurement", "Corrugated Board")

    _assert_six_distinct_suppliers(data)


def test_non_streamlit_default_remains_unexpanded(monkeypatch):
    fake_streamlit = SimpleNamespace(runtime=SimpleNamespace(exists=lambda: False))
    monkeypatch.setitem(sys.modules, "streamlit", fake_streamlit)

    data = get_demo_data("Packaging Procurement", "Corrugated Board")

    _assert_three_suppliers(data)


def test_direct_deterministic_fixtures_retain_historical_three_row_shape():
    _assert_three_suppliers(get_demo_suppliers())
    _assert_three_suppliers(get_flexible_laminate_demo_suppliers("PET / PE"))
    _assert_three_suppliers(get_kraft_paper_demo_suppliers())
    _assert_three_suppliers(get_steel_demo_suppliers())
    _assert_three_suppliers(get_raw_material_demo_suppliers("PET Resin"))
