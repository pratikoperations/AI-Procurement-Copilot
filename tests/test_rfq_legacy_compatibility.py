from decimal import Decimal
from types import SimpleNamespace

import pandas as pd
import pytest

from modules.rfq_legacy_compatibility import (
    GOVERNED_RANKING_INPUTS_NOT_CANONICAL,
    assess_legacy_compatibility,
    display_currency_frame,
)


def quote(row_id, supplier, source_currency="USD", comparison_currency="USD", source_price=10, normalized_price=10, original=None):
    record = SimpleNamespace(
        canonical_values={"RFQ_NUMBER": "R1", "RFQ_ITEM": "10", "SUPPLIER_NAME": supplier},
        original_values=original or {},
        provenance=SimpleNamespace(source_row_id=row_id),
    )
    normalized = {
        "COMPARISON_CURRENCY": comparison_currency,
        "NORMALIZED_UNIT_PRICE": Decimal(str(normalized_price)),
        "SOURCE_CURRENCY": source_currency,
        "SOURCE_PRICE": Decimal(str(source_price)),
        "EXCHANGE_RATE_USED": Decimal("1"),
        "EXCHANGE_RATE_DATE_USED": "2026-07-29",
        "COMPARISON_UOM": "EA",
    }
    return SimpleNamespace(record=record, normalization=SimpleNamespace(normalized_values=normalized), eligible_for_analysis=True)


def orchestration(*quotes, status="ELIGIBLE_FOR_ANALYSIS"):
    return SimpleNamespace(enriched_quotes=quotes, eligibility_status=status)


def test_governed_review_never_produces_analytical_dataframe():
    result = assess_legacy_compatibility(orchestration(quote("Q1", "A"), quote("Q2", "B")), selected_rfq_number="R1", selected_rfq_item="10")
    assert not result.compatible
    assert result.dataframe is None
    assert GOVERNED_RANKING_INPUTS_NOT_CANONICAL in result.blockers


def test_ignored_original_columns_remain_provenance_only_even_when_malformed():
    malicious = {"OTIF %": "high", "Quality PPM": -500, "Audit Score": 500}
    result = assess_legacy_compatibility(orchestration(quote("Q1", "A", original=malicious), quote("Q2", "B")), selected_rfq_number="R1", selected_rfq_item="10")
    assert result.dataframe is None
    assert not any(item.source_field in malicious for item in result.manifest if item.handoff_permitted)
    assert any(item.value_origin == "PROVENANCE_ONLY" for item in result.manifest)


def test_inr_workbook_basis_is_not_labelled_usd():
    result = assess_legacy_compatibility(orchestration(quote("Q1", "A", "INR", "INR", 830, 830), quote("Q2", "B", "USD", "INR", 10, 830)), selected_rfq_number="R1", selected_rfq_item="10")
    assert result.workbook_comparison_currency == "INR"
    assert result.dataframe is None
    assert all(item.legacy_field != "Quoted Unit Price USD" for item in result.manifest)


def test_source_currency_and_review_normalization_are_preserved_in_manifest():
    result = assess_legacy_compatibility(orchestration(quote("Q1", "A", "INR", "INR", 830, 830), quote("Q2", "B", "USD", "INR", 10, 830)), selected_rfq_number="R1", selected_rfq_item="10")
    fields = {item.legacy_field for item in result.manifest}
    assert {"Source Currency", "Source Price", "Workbook Comparison Currency", "Normalized Unit Price"}.issubset(fields)


def test_display_modes_do_not_modify_canonical_dataframe():
    canonical = pd.DataFrame({"Quoted Unit Price USD": [10.0], "Supplier": ["A"]})
    usd = display_currency_frame(canonical, "USD", 83)
    inr = display_currency_frame(canonical, "INR", 83)
    both = display_currency_frame(canonical, "Both", 83)
    assert "Quoted Unit Price INR" not in usd
    assert inr["Quoted Unit Price INR"].iloc[0] == 830
    assert both["Quoted Unit Price INR"].iloc[0] == 830
    assert list(canonical.columns) == ["Quoted Unit Price USD", "Supplier"]


def test_inr_display_requires_positive_rate():
    with pytest.raises(ValueError, match="DISPLAY_FX_RATE_REQUIRED"):
        display_currency_frame(pd.DataFrame({"Quoted Unit Price USD": [10.0]}), "INR", 0)
