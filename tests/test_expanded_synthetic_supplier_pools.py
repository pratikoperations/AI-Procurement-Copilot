"""Focused assurance for expanded synthetic supplier pools."""

from modules.data_loader import get_demo_data


def _assert_six_distinct_suppliers(data):
    assert len(data) == 6
    assert data["Supplier"].nunique() == 6
    assert data["Quoted Unit Price USD"].nunique(dropna=False) >= 4
    assert data["Lead Time Days"].nunique() >= 4
    assert data["OTIF %"].nunique() >= 4


def test_general_packaging_application_route_has_six_differentiated_suppliers():
    data = get_demo_data("Packaging Procurement", "Corrugated Board")
    _assert_six_distinct_suppliers(data)
    assert set(data["Risk Category"]) >= {"Low", "Medium"}


def test_flexible_laminates_application_route_has_six_suppliers_for_every_structure():
    for structure in ("PET / PE", "PET / MetPET / PE", "BOPP / CPP"):
        data = get_demo_data("Packaging Procurement", "Flexible Laminates", selected_structure=structure)
        _assert_six_distinct_suppliers(data)
        assert data.attrs["selected_laminate_structure"] == structure
        assert {"Conditional", "Not approved"} <= set(data["Application Approval Status"])


def test_kraft_paper_application_route_has_six_differentiated_suppliers():
    data = get_demo_data("Raw Material Procurement", "Kraft Paper")
    _assert_six_distinct_suppliers(data)
    assert set(data["Kraft Variant"]) == {"Recycled Kraft", "Virgin Kraft"}
    assert "Conditional demonstration assumption" in set(data["Corrugated Linkage"])


def test_steel_application_route_has_six_suppliers_and_ineligible_examples():
    data = get_demo_data("Raw Material Procurement", "Steel")
    _assert_six_distinct_suppliers(data)
    assert set(data["Currency"]) == {"USD", "INR"}
    assert "Not approved" in set(data["Application Approval"])
    assert "No" in set(data["Paint Line Capability"])
    assert data.attrs["source_label"] == "Synthetic controlled demonstration data"
