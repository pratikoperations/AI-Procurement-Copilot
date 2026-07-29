from datetime import date, datetime
from types import SimpleNamespace

from modules.rfq_orchestration import orchestrate_adapter_result


def record(row_id, supplier="S1", material="M1", requested=100, description="PET Resin", group="RM"):
    values = {
        "RFQ_NUMBER": "R1",
        "RFQ_ITEM": "10",
        "SUPPLIER_ID": supplier,
        "MATERIAL_ID": material,
        "MATERIAL_GROUP": group,
        "MATERIAL_DESCRIPTION": description,
        "REQUESTED_QUANTITY": requested,
        "QUOTED_QUANTITY": requested,
        "FULL_QUANTITY_AVAILABLE": True,
        "BASE_UNIT_PRICE": 10,
        "PRICE_UNIT": 1,
        "QUOTATION_UOM": "EA",
        "COMPARISON_UOM": "EA",
        "CURRENCY": "INR",
        "VALIDITY_END_DATE": date(2026, 8, 1),
        "INCOTERMS_CODE": "DAP",
        "LEAD_TIME_DAYS": 5,
        "TECHNICALLY_APPROVED": True,
        "RISK_SCORE": 80,
        "ESG_SCORE": 70,
        "SOURCE_EXTRACTED_AT": datetime(2026, 7, 1),
    }
    return SimpleNamespace(
        canonical_values=values,
        provenance=SimpleNamespace(source_row_id=row_id),
        eligible_for_analysis=True,
        row_valid=True,
    )


def history(row_id="H1", material="M1", description="PET Resin", group="RM", extracted=datetime(2026, 7, 20)):
    values = {
        "MATERIAL_ID": material,
        "MATERIAL_GROUP": group,
        "MATERIAL_DESCRIPTION": description,
        "ORDER_QUANTITY": 100,
        "NET_PRICE": 9,
        "PRICE_UNIT": 1,
        "ORDER_UOM": "EA",
        "COMPARISON_UOM": "EA",
        "CURRENCY": "INR",
        "PO_DATE": date(2026, 6, 1),
        "SOURCE_EXTRACTED_AT": extracted,
    }
    return SimpleNamespace(
        canonical_values=values,
        provenance=SimpleNamespace(source_row_id=row_id),
        row_valid=True,
    )


def adapter(quotes, findings=(), metadata=None, history_rows=(), mode="QUICK_RFQ"):
    return SimpleNamespace(
        rfq_quotes=tuple(quotes),
        po_history=tuple(history_rows),
        findings=tuple(findings),
        upload_metadata=metadata or {"BASE_CURRENCY": "INR", "UPLOAD_CREATED_AT": datetime(2026, 7, 29)},
        mode=mode,
    )


def full_metadata():
    return {
        "BASE_CURRENCY": "INR",
        "UPLOAD_CREATED_AT": datetime(2026, 7, 29),
        "HISTORY_START_DATE": date(2026, 1, 1),
        "HISTORY_END_DATE": date(2026, 7, 29),
        "HISTORY_SOURCE_TRANSACTION": "ME80FN",
    }


def orchestrate_full(quotes, history_rows, **kwargs):
    return orchestrate_adapter_result(
        adapter(quotes, metadata=full_metadata(), history_rows=history_rows, mode="FULL_SOURCING_REVIEW"),
        evaluation_date=date(2026, 7, 29),
        **kwargs,
    )


def test_orchestrator_preserves_adapter_result():
    source = adapter([record("Q1"), record("Q2", "S2")])
    assert orchestrate_adapter_result(source, evaluation_date=date(2026, 7, 29)).adapter_result is source


def test_adapter_blocker_is_preserved():
    finding = SimpleNamespace(severity="Blocking", code="ADAPTER_BLOCK")
    result = orchestrate_adapter_result(adapter([record("Q1")], findings=(finding,)), evaluation_date=date(2026, 7, 29))
    assert result.eligibility_status == "BLOCKED" and "ADAPTER_BLOCK" in result.blockers


def test_missing_currency_blocks_without_usd_default():
    source = adapter([record("Q1")], metadata={"UPLOAD_CREATED_AT": datetime(2026, 7, 29)})
    result = orchestrate_adapter_result(source, evaluation_date=date(2026, 7, 29))
    assert result.comparison_currency is None and result.eligibility_status == "BLOCKED"


def test_expired_record_blocks():
    quote = record("Q1")
    quote.canonical_values["VALIDITY_END_DATE"] = date(2026, 7, 1)
    assert orchestrate_adapter_result(adapter([quote]), evaluation_date=date(2026, 7, 29)).eligibility_status == "BLOCKED"


def test_exact_material_history_match():
    result = orchestrate_full([record("Q1")], [history()])
    assert result.enriched_quotes[0].historical_match.method == "EXACT_MATERIAL_ID"


def test_material_group_description_match():
    quote = record("Q1", material=None, description=" PET   Resin ", group="RM")
    result = orchestrate_full([quote], [history(material=None, description="pet resin", group="RM")], approved_free_text_row_ids={"Q1"})
    assert result.enriched_quotes[0].historical_match.method == "MATERIAL_GROUP_DESCRIPTION"


def test_approved_mapped_identifier_match():
    quote = record("Q1", material="NEW")
    result = orchestrate_full([quote], [history(material="OLD")], approved_history_mappings={"Q1": "H1"})
    assert result.enriched_quotes[0].historical_match.method == "APPROVED_MAPPED_IDENTIFIER"


def test_manual_confirmation_match():
    quote = record("Q1", material="NEW")
    result = orchestrate_full([quote], [history(material="OLD")], manual_history_confirmations={("Q1", "H1")})
    assert result.enriched_quotes[0].historical_match.method == "MANUAL_CONFIRMATION"


def test_ambiguous_exact_candidates_do_not_match():
    result = orchestrate_full([record("Q1")], [history("H1"), history("H2")])
    assert not result.enriched_quotes[0].historical_match.matched


def test_no_history_match_receives_no_history_credit():
    result = orchestrate_full([record("Q1", material="M2")], [history(material="M1")])
    assert result.enriched_quotes[0].evidence.dimension_results["historical_benchmark"] is False


def test_stale_history_remains_visible_but_receives_no_credit():
    result = orchestrate_full([record("Q1")], [history(extracted=datetime(2026, 4, 1))])
    assert len(result.enriched_history) == 1
    assert not result.enriched_history[0].eligible_for_analysis
    assert result.enriched_quotes[0].evidence.dimension_results["historical_benchmark"] is False
    assert "HISTORY_STALE" in result.warnings


def test_current_history_receives_credit():
    result = orchestrate_full([record("Q1")], [history()])
    assert result.enriched_quotes[0].evidence.dimension_results["historical_benchmark"] is True


def test_requested_quantity_conflict_blocks_and_is_order_independent():
    quotes_a = [record("Q1", "S1", requested=100), record("Q2", "S2", requested=200)]
    quotes_b = list(reversed(quotes_a))
    first = orchestrate_adapter_result(adapter(quotes_a), evaluation_date=date(2026, 7, 29))
    second = orchestrate_adapter_result(adapter(quotes_b), evaluation_date=date(2026, 7, 29))
    assert "RFQ_ITEM_REQUESTED_QUANTITY_CONFLICT" in first.blockers
    assert first.blockers == second.blockers
    assert first.eligibility_status == second.eligibility_status == "BLOCKED"


def test_consistent_requested_quantity_is_quantity_weighted():
    result = orchestrate_adapter_result(
        adapter([record("Q1", "S1", requested=100), record("Q2", "S2", requested=100)]),
        evaluation_date=date(2026, 7, 29),
    )
    assert result.event_aggregation_method == "REQUESTED_QUANTITY_WEIGHTED"


def test_full_evidence_reaches_gate_with_current_history():
    result = orchestrate_full([record("Q1"), record("Q2", "S2")], [history()])
    assert result.event_coverage_percent >= 70