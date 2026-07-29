from datetime import date, datetime
from types import SimpleNamespace

from modules.rfq_orchestration import orchestrate_adapter_result


def record(row_id, supplier="S1", material="M1", requested=100, description="PET Resin", group="RM"):
    values = {
        "RFQ_NUMBER": "R1", "RFQ_ITEM": "10", "SUPPLIER_ID": supplier,
        "MATERIAL_ID": material, "MATERIAL_GROUP": group, "MATERIAL_DESCRIPTION": description,
        "REQUESTED_QUANTITY": requested, "QUOTED_QUANTITY": requested,
        "FULL_QUANTITY_AVAILABLE": True, "BASE_UNIT_PRICE": 10, "PRICE_UNIT": 1,
        "QUOTATION_UOM": "EA", "COMPARISON_UOM": "EA", "CURRENCY": "INR",
        "VALIDITY_END_DATE": date(2026, 8, 1), "INCOTERMS_CODE": "DAP",
        "LEAD_TIME_DAYS": 5, "TECHNICALLY_APPROVED": True, "RISK_SCORE": 80,
        "ESG_SCORE": 70, "SOURCE_EXTRACTED_AT": datetime(2026, 7, 1),
    }
    return SimpleNamespace(canonical_values=values, provenance=SimpleNamespace(source_row_id=row_id), eligible_for_analysis=True, row_valid=True)


def history(row_id="H1", material="M1", description="PET Resin", group="RM", extracted=datetime(2026, 7, 20), po_date=date(2026, 6, 1)):
    values = {
        "MATERIAL_ID": material, "MATERIAL_GROUP": group, "MATERIAL_DESCRIPTION": description,
        "ORDER_QUANTITY": 100, "NET_PRICE": 9, "PRICE_UNIT": 1,
        "ORDER_UOM": "EA", "COMPARISON_UOM": "EA", "CURRENCY": "INR",
        "PO_DATE": po_date, "SOURCE_EXTRACTED_AT": extracted,
    }
    return SimpleNamespace(canonical_values=values, provenance=SimpleNamespace(source_row_id=row_id), row_valid=True)


def adapter(quotes, findings=(), metadata=None, history_rows=(), mode="QUICK_RFQ"):
    return SimpleNamespace(rfq_quotes=tuple(quotes), po_history=tuple(history_rows), findings=tuple(findings), upload_metadata=metadata or {"BASE_CURRENCY": "INR", "UPLOAD_CREATED_AT": datetime(2026, 7, 29)}, mode=mode)


def full_metadata():
    return {"BASE_CURRENCY": "INR", "UPLOAD_CREATED_AT": datetime(2026, 7, 29), "HISTORY_START_DATE": date(2026, 1, 1), "HISTORY_END_DATE": date(2026, 7, 29), "HISTORY_SOURCE_TRANSACTION": "ME80FN"}


def orchestrate_full(quotes, history_rows, **kwargs):
    return orchestrate_adapter_result(adapter(quotes, metadata=full_metadata(), history_rows=history_rows, mode="FULL_SOURCING_REVIEW"), evaluation_date=date(2026, 7, 29), **kwargs)


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
    assert orchestrate_full([record("Q1")], [history()]).enriched_quotes[0].historical_match.method == "EXACT_MATERIAL_ID"


def test_material_group_description_match():
    quote = record("Q1", material=None, description=" PET   Resin ", group="RM")
    result = orchestrate_full([quote], [history(material=None, description="pet resin", group="RM")], approved_free_text_row_ids={"Q1"})
    assert result.enriched_quotes[0].historical_match.method == "MATERIAL_GROUP_DESCRIPTION"


def test_mapping_resolves_ambiguous_exact_matches():
    result = orchestrate_full([record("Q1")], [history("H1"), history("H2")], approved_history_mappings={"Q1": "H2"})
    assert result.enriched_quotes[0].historical_match.method == "APPROVED_MAPPED_IDENTIFIER"
    assert result.enriched_quotes[0].historical_match.matched_history_row_id == "H2"


def test_manual_confirmation_resolves_ambiguous_descriptive_matches():
    quote = record("Q1", material="NEW", description="Resin Grade", group="RM")
    rows = [history("H1", material="OLD1", description="Resin Grade", group="RM"), history("H2", material="OLD2", description="Resin Grade", group="RM")]
    result = orchestrate_full([quote], rows, manual_history_confirmations={("Q1", "H1")})
    assert result.enriched_quotes[0].historical_match.method == "MANUAL_CONFIRMATION"


def test_unresolved_ambiguity_emits_warning_and_no_credit():
    result = orchestrate_full([record("Q1")], [history("H1"), history("H2")])
    assert not result.enriched_quotes[0].historical_match.matched
    assert "HISTORICAL_MATCH_AMBIGUOUS" in result.warnings
    assert result.enriched_quotes[0].evidence.dimension_results["historical_benchmark"] is False


def test_mixed_current_and_stale_history_does_not_reactivate_stale_row():
    rows = [history("H1", extracted=datetime(2026, 4, 1)), history("H2", extracted=datetime(2026, 7, 20))]
    result = orchestrate_full([record("Q1")], rows)
    assert not result.enriched_history[0].eligible_for_analysis
    assert result.enriched_history[1].eligible_for_analysis
    assert result.enriched_quotes[0].historical_match.matched_history_row_id == "H2"


def test_invalid_out_of_window_history_does_not_block_event():
    row = history(po_date=date(2025, 12, 1))
    row.canonical_values["PRICE_UNIT"] = 0
    result = orchestrate_full([record("Q1")], [row])
    assert "PRICE_UNIT_INVALID" not in result.blockers


def test_invalid_stale_history_does_not_block_event():
    row = history(extracted=datetime(2026, 4, 1))
    row.canonical_values["PRICE_UNIT"] = 0
    result = orchestrate_full([record("Q1")], [row])
    assert "PRICE_UNIT_INVALID" not in result.blockers


def test_invalid_optional_quick_history_does_not_block_event():
    row = history()
    row.canonical_values["PRICE_UNIT"] = 0
    result = orchestrate_adapter_result(adapter([record("Q1")], history_rows=[row]), evaluation_date=date(2026, 7, 29))
    assert "PRICE_UNIT_INVALID" not in result.blockers


def test_applicable_invalid_full_review_history_gets_governed_warning():
    row = history()
    row.canonical_values["PRICE_UNIT"] = 0
    result = orchestrate_full([record("Q1")], [row])
    assert "HISTORY_NORMALIZATION_INVALID" in result.warnings
    assert result.enriched_quotes[0].evidence.dimension_results["historical_benchmark"] is False


def test_zero_price_warning_and_comparable_evidence_suppression():
    quote = record("Q1")
    quote.canonical_values["BASE_UNIT_PRICE"] = 0
    result = orchestrate_adapter_result(adapter([quote]), evaluation_date=date(2026, 7, 29))
    assert "ZERO_PRICE_REQUIRES_CLASSIFICATION" in result.warnings
    assert result.enriched_quotes[0].evidence.dimension_results["comparable_price"] is False


def test_requested_quantity_conflict_blocks_and_is_order_independent():
    quotes_a = [record("Q1", "S1", requested=100), record("Q2", "S2", requested=200)]
    first = orchestrate_adapter_result(adapter(quotes_a), evaluation_date=date(2026, 7, 29))
    second = orchestrate_adapter_result(adapter(list(reversed(quotes_a))), evaluation_date=date(2026, 7, 29))
    assert "RFQ_ITEM_REQUESTED_QUANTITY_CONFLICT" in first.blockers
    assert first.blockers == second.blockers
    assert first.eligibility_status == second.eligibility_status == "BLOCKED"


def test_consistent_requested_quantity_is_quantity_weighted():
    result = orchestrate_adapter_result(adapter([record("Q1", "S1"), record("Q2", "S2")]), evaluation_date=date(2026, 7, 29))
    assert result.event_aggregation_method == "REQUESTED_QUANTITY_WEIGHTED"


def test_full_evidence_reaches_gate_with_current_history():
    assert orchestrate_full([record("Q1"), record("Q2", "S2")], [history()]).event_coverage_percent >= 70
