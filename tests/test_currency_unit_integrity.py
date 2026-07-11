import pandas as pd

from modules.currency_unit_governance import normalize_comparison_basis, validate_category_unit
from modules.data_loader import get_demo_data


def test_raw_material_demo_is_usd_and_kg():
    df = get_demo_data("Raw Material Procurement", "PET Resin")
    assert set(df["Currency"]) == {"USD"}
    assert set(df["Unit"]) == {"kg"}


def test_inr_converts_to_usd_with_valid_fx():
    df = pd.DataFrame([{"Supplier":"A","Quoted Unit Price USD":83.0,"Currency":"INR","Unit":"kg"}])
    out = normalize_comparison_basis(df, 83)
    assert out.loc[0, "Original Currency"] == "INR"
    assert out.loc[0, "Normalized Currency"] == "USD"
    assert out.loc[0, "Normalized Unit Price"] == 1.0
    assert out.attrs["currency_unit_governance"]["normalized"] is True


def test_unsupported_currency_is_blocked():
    df = pd.DataFrame([{"Supplier":"A","Quoted Unit Price USD":1.0,"Currency":"EUR","Unit":"kg"}])
    out = normalize_comparison_basis(df, 83)
    assert out.attrs["currency_unit_governance"]["blockers"]


def test_pet_resin_rejects_non_kg_unit():
    df = pd.DataFrame([{"Unit":"piece"}])
    assert validate_category_unit(df, "Raw Material Procurement", "PET Resin")
