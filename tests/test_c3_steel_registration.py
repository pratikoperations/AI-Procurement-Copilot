"""C3.1 governed Steel registration and synthetic supplier-data tests."""

from modules.commodity_library import get_commodity_profile
from modules.data_loader import get_demo_data, get_raw_material_demo_suppliers, get_steel_demo_suppliers


EXPECTED_PROFILES = {
    "CR_COIL_COMMERCIAL",
    "GI_COIL_Z120",
    "PPGI_COIL_Z120",
}

REQUIRED_CAPABILITY_COLUMNS = {
    "Supported Steel Profiles",
    "Controlled Grade Families",
    "Thickness Min mm",
    "Thickness Max mm",
    "Width Min mm",
    "Width Max mm",
    "Zinc Capability Max g/m²",
    "Paint Line Capability",
    "Surface Capability",
    "Coil Weight Min MT",
    "Coil Weight Max MT",
    "Supplier or Mill Approval",
    "Application Approval",
    "Test Certificate Availability",
    "Supplier Capacity",
    "Capacity Utilisation %",
    "Mill Allocation %",
    "Import Dependency %",
    "Supplier Concentration %",
    "Quality Continuity Score",
}


def test_steel_registry_contains_exact_controlled_profiles():
    profile = get_commodity_profile("Raw Material Procurement", "Steel")
    assert set(profile["profiles"]) == EXPECTED_PROFILES
    assert profile["unit"] == "kg"
    assert profile["calculation_currency"] == "USD"
    assert profile["comparison_unit"] == "USD/kg"
    assert profile["display_modes"] == ["USD", "INR", "Both"]
    assert profile["accepted_quote_currencies"] == ["USD", "INR"]


def test_controlled_profile_attributes_are_preserved():
    profiles = get_commodity_profile("Raw Material Procurement", "Steel")["profiles"]
    cr = profiles["CR_COIL_COMMERCIAL"]
    gi = profiles["GI_COIL_Z120"]
    ppgi = profiles["PPGI_COIL_Z120"]

    assert (cr["thickness_mm"], cr["width_min_mm"], cr["width_max_mm"]) == (0.80, 1000, 1250)
    assert (cr["zinc_coating_gsm"], cr["topcoat_micron"], cr["backcoat_micron"]) == (0, 0, 0)
    assert (gi["thickness_mm"], gi["zinc_coating_gsm"]) == (0.60, 120)
    assert (gi["topcoat_micron"], gi["backcoat_micron"]) == (0, 0)
    assert (ppgi["thickness_mm"], ppgi["zinc_coating_gsm"]) == (0.50, 120)
    assert (ppgi["topcoat_micron"], ppgi["backcoat_micron"]) == (20, 5)


def test_grade_families_and_coil_weight_bands_are_controlled_and_synthetic():
    profiles = get_commodity_profile("Raw Material Procurement", "Steel")["profiles"]
    for profile in profiles.values():
        assert "demonstration family" in profile["grade_family"]
        assert len(profile["coil_weight_band_mt"]) == 2
        assert profile["coil_weight_band_mt"][0] > 0
        assert profile["coil_weight_band_mt"][1] > profile["coil_weight_band_mt"][0]


def test_dedicated_steel_dataset_contains_exactly_three_suppliers():
    data = get_steel_demo_suppliers()
    assert len(data) == 3
    assert data["Supplier"].is_unique
    assert set(data["Material"]) == {"Steel"}
    assert set(data["Unit"]) == {"kg"}


def test_steel_dataset_includes_usd_and_inr_quotations():
    data = get_steel_demo_suppliers()
    assert set(data["Quotation Currency"]) == {"USD", "INR"}
    assert set(data["Currency"]) == {"USD", "INR"}
    assert (data["Quoted Unit Price"] > 0).all()


def test_steel_supplier_capability_schema_is_complete():
    data = get_steel_demo_suppliers()
    assert REQUIRED_CAPABILITY_COLUMNS.issubset(data.columns)
    assert data[list(REQUIRED_CAPABILITY_COLUMNS)].notna().all().all()


def test_supplier_design_contains_competitive_low_risk_and_ineligible_cases():
    data = get_steel_demo_suppliers()
    intents = set(data["Eligibility Design Intent"])
    assert "Eligible competitive supplier" in intents
    assert "Eligible higher-cost lower-risk supplier" in intents
    assert "Lower-priced technically ineligible or conditional supplier" in intents

    conditional = data.loc[data["Supplier"] == "Global Coil Trading"].iloc[0]
    assert conditional["Application Approval"] == "Conditional"
    assert conditional["Test Certificate Availability"] == "Pending"
    assert conditional["Paint Line Capability"] == "No"
    assert conditional["Zinc Capability Max g/m²"] < 120


def test_controlled_source_and_claim_boundaries_are_present():
    data = get_steel_demo_suppliers()
    assert set(data["Source Label"]) == {"Synthetic controlled demonstration data"}
    assert data["Evidence Boundary"].str.contains("not audited supplier evidence", case=False).all()
    assert data["Evidence Boundary"].str.contains("not live market data", case=False).all()
    assert data["Evidence Boundary"].str.contains("not technical certification", case=False).all()
    assert data.attrs["assumption_profile_version"] == "C3.1-STEEL-v1"


def test_raw_material_route_uses_dedicated_steel_dataset_not_generic_names():
    data = get_raw_material_demo_suppliers("Steel")
    assert set(data["Supplier"]) == {
        "Bharat Steelworks Ltd",
        "PrimeCoated Metals",
        "Global Coil Trading",
    }
    assert "Indus Materials Ltd" not in set(data["Supplier"])
    assert "Global Commodity Corp" not in set(data["Supplier"])


def test_get_demo_data_preserves_c3_metadata_and_dedicated_routing():
    data = get_demo_data("Raw Material Procurement", "Steel")
    assert len(data) == 3
    assert data.attrs["category"] == "Raw Material Procurement"
    assert data.attrs["commodity"] == "Steel"
    assert data.attrs["source_label"] == "Synthetic controlled demonstration data"
    assert data.attrs["assumption_profile_version"] == "C3.1-STEEL-v1"


def test_c1_and_c2_profiles_remain_registered_and_unchanged_in_identity():
    kraft = get_commodity_profile("Raw Material Procurement", "Kraft Paper")
    laminate = get_commodity_profile("Packaging Procurement", "Flexible Laminates")
    assert kraft["assumption_profile_version"] == "C1.0"
    assert kraft["variants"] == ["Recycled Kraft", "Virgin Kraft"]
    assert laminate["assumption_profile_version"] == "C2.0"
    assert laminate["structures"] == ["PET / PE", "PET / MetPET / PE", "BOPP / CPP"]
