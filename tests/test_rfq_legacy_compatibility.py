from decimal import Decimal
from types import SimpleNamespace

import pandas as pd
import pytest

from modules.rfq_legacy_compatibility import (
    CANONICAL_ENGINE_CURRENCY,
    assess_legacy_compatibility,
    display_currency_frame,
)

RANKING = {
    "OTIF %": 95,
    "Quality PPM": 500,
    "Audit Score": 85,
    "Complaint Rate %": 1.0,
    "Capacity Buffer %": 20,
    "Recyclability": 90,
    "Certification": 85,
    "Carbon Score": 75,
    "EPR Readiness": 80,
    "PCR Content %": 20,
}


def quote(row_id, supplier, source_currency="USD", source_price=10, fx=1, fx_date="2026-07-29", ranking=True):
    values = {
        "RFQ_NUMBER": "R1",
        "RFQ_ITEM": "10",
        "SUPPLIER_NAME": supplier,
        "MINIMUM_ORDER_QUANTITY": Decimal("100"),
        "LEAD_TIME_DAYS": 10,
        "PAYMENT_TERMS_CODE": "NET30",
        "INCOTERMS_CODE": "DDP",
        "MATERIAL_DESCRIPTION": "Bottle",
    }
    original = dict(RANKING) if ranking else {}
    record = SimpleNamespace(
        canonical_values=values,
        original_values=original,
        provenance=SimpleNamespace(source_row_id=row_id),
    )
    normalized = {
        "COMPARISON_CURRENCY": "USD",
        "NORMALIZED_UNIT_PRICE": Decimal("10"),
        "SOURCE_CURRENCY": source_currency,
        "SOURCE_PRICE": Decimal(str(source_price)),
        "EXCHANGE_RATE_USED": Decimal(str(fx)),
        "EXCHANGE_RATE_DATE_USED": fx_date,
        "COMPARISON_UOM": "piece",
    }
    return SimpleNamespace(record=record, normalization=SimpleNamespace(normalized_values=normalized), eligible_for_analysis=True)


def orchestration(*quotes, status="ELIGIBLE_FOR_ANALYSIS"):
    return SimpleNamespace(enriched_quotes=quotes, eligibility_status=status)


def test_usd_source_builds_canonical_usd_dataframe():
    result = assess_legacy_compatibility(orchestration(quote("Q1", "A"), quote("Q2", "B")), selected_rfq_number="R1", selected_rfq_item="10")
    assert result.compatible
    assert result.dataframe is not None
    assert set(result.dataframe["Currency"]) == {CANONICAL_ENGINE_CURRENCY}
    assert set(result.dataframe["Original Currency"]) == {"USD"}


def test_inr_source_preserves_source_and_uses_canonical_usd():
    result = assess_legacy_compatibility(orchestration(quote("Q1", "A", "INR", 830, 83), quote("Q2", "B", "USD", 10, 1)), selected_rfq_number="R1", selected_rfq_item="10")
    assert result.compatible
    assert list(result.dataframe["Original Currency"]) == ["INR", "USD"]
    assert set(result.dataframe["Currency"]) == {"USD"}
    assert list(result.dataframe["Quoted Unit Price USD"]) == [10.0, 10.0]


def test_missing_ranking_inputs_fail_closed():
    result = assess_legacy_compatibility(orchestration(quote("Q1", "A", ranking=False), quote("Q2", "B")), selected_rfq_number="R1", selected_rfq_item="10")
    assert not result.compatible
    assert any(code.startswith("RANKING_INPUT_MISSING:Q1") for code in result.blockers)


def test_non_usd_canonical_value_is_rejected():
    item = quote("Q1", "A")
    item.normalization.normalized_values["COMPARISON_CURRENCY"] = "INR"
    result = assess_legacy_compatibility(orchestration(item, quote("Q2", "B")), selected_rfq_number="R1", selected_rfq_item="10")
    assert not result.compatible
    assert "CANONICAL_USD_ENGINE_VALUE_REQUIRED" in result.blockers


def test_insufficient_evidence_never_hands_off():
    result = assess_legacy_compatibility(orchestration(quote("Q1", "A"), quote("Q2", "B"), status="INSUFFICIENT_EVIDENCE"), selected_rfq_number="R1", selected_rfq_item="10")
    assert not result.compatible
    assert "ORCHESTRATION_INSUFFICIENT_EVIDENCE" in result.blockers


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
