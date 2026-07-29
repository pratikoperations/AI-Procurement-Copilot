from datetime import date, datetime
from types import SimpleNamespace

from modules.rfq_conditional_rules import evaluate_conditional_rules, evaluate_history_staleness, resolve_evaluation_date


def rec(row_id, values, eligible=True):
    return SimpleNamespace(canonical_values=values, provenance=SimpleNamespace(source_row_id=row_id), eligible_for_analysis=eligible, row_valid=eligible)


def result(mode="QUICK_RFQ", metadata=None, quotes=(), history=()):
    return SimpleNamespace(mode=mode, upload_metadata=metadata, rfq_quotes=quotes, po_history=history)


def test_evaluation_date_precedence():
    adapter = result(metadata={"UPLOAD_CREATED_AT": datetime(2026, 7, 2), "EXTRACTED_AT": datetime(2026, 7, 1)})
    assert resolve_evaluation_date(adapter.upload_metadata, (), date(2026, 7, 3))[1] == "EXPLICIT_INPUT"
    assert resolve_evaluation_date(adapter.upload_metadata, ())[1] == "UPLOAD_CREATED_AT"


def test_source_extracted_date_precedes_system_date():
    quote = rec("Q1", {"SOURCE_EXTRACTED_AT": datetime(2026, 7, 5)})
    assert resolve_evaluation_date({}, (quote,), today=date(2026, 7, 29))[1] == "LATEST_SOURCE_EXTRACTED_AT"


def test_system_date_warns():
    _, source, findings = resolve_evaluation_date({}, (), today=date(2026, 7, 29))
    assert source == "SYSTEM_DATE" and findings[0].code == "SYSTEM_DATE_FALLBACK"


def test_expired_quote_is_ineligible():
    quote = rec("Q1", {"MATERIAL_ID": "M1", "VALIDITY_END_DATE": date(2026, 7, 1)})
    flags, _, findings = evaluate_conditional_rules(result(quotes=(quote,)), date(2026, 7, 29))
    assert not flags["Q1"] and any(finding.code == "QUOTATION_EXPIRED" for finding in findings)


def test_material_id_requires_approval():
    quote = rec("Q1", {"VALIDITY_END_DATE": date(2026, 8, 1)})
    flags, _, _ = evaluate_conditional_rules(result(quotes=(quote,)), date(2026, 7, 29))
    assert not flags["Q1"]
    flags, _, _ = evaluate_conditional_rules(result(quotes=(quote,)), date(2026, 7, 29), approved_free_text_row_ids={"Q1"})
    assert flags["Q1"]


def test_full_review_requires_metadata():
    _, _, findings = evaluate_conditional_rules(result(mode="FULL_SOURCING_REVIEW"), date(2026, 7, 29))
    assert sum(finding.code == "FULL_REVIEW_HISTORY_METADATA_REQUIRED" for finding in findings) == 3


def test_out_of_window_history_is_ineligible():
    history = rec("H1", {"PO_DATE": date(2025, 12, 31), "SOURCE_EXTRACTED_AT": datetime(2026, 7, 20)})
    adapter = result(mode="FULL_SOURCING_REVIEW", metadata={"HISTORY_START_DATE": date(2026, 1, 1), "HISTORY_END_DATE": date(2026, 7, 29), "HISTORY_SOURCE_TRANSACTION": "ME80FN"}, history=(history,))
    _, flags, findings = evaluate_conditional_rules(adapter, date(2026, 7, 29))
    assert not flags["H1"] and any(finding.code == "HISTORY_ROW_OUT_OF_WINDOW" for finding in findings)


def test_current_eligible_history_is_not_stale():
    history = rec("H1", {"SOURCE_EXTRACTED_AT": datetime(2026, 7, 20)})
    current, findings = evaluate_history_staleness((history,), {"H1"}, date(2026, 7, 29))
    assert current == {"H1"} and not findings


def test_all_eligible_history_stale_gets_no_current_rows():
    history = rec("H1", {"SOURCE_EXTRACTED_AT": datetime(2026, 4, 1)})
    current, findings = evaluate_history_staleness((history,), {"H1"}, date(2026, 7, 29))
    assert current == set() and findings[0].code == "HISTORY_STALE"


def test_mixed_current_and_stale_history_keeps_only_current_row():
    stale = rec("H1", {"SOURCE_EXTRACTED_AT": datetime(2026, 4, 1)})
    current_row = rec("H2", {"SOURCE_EXTRACTED_AT": datetime(2026, 7, 25)})
    current, findings = evaluate_history_staleness((stale, current_row), {"H1", "H2"}, date(2026, 7, 29))
    assert current == {"H2"}
    assert findings[0].code == "HISTORY_STALE"


def test_newer_ineligible_row_does_not_mask_stale_eligible_history():
    stale = rec("H1", {"SOURCE_EXTRACTED_AT": datetime(2026, 4, 1)})
    newer = rec("H2", {"SOURCE_EXTRACTED_AT": datetime(2026, 7, 25)})
    current, findings = evaluate_history_staleness((stale, newer), {"H1"}, date(2026, 7, 29))
    assert current == set() and findings[0].code == "HISTORY_STALE"


def test_no_eligible_history_returns_no_current_rows_without_false_stale_warning():
    history = rec("H1", {"SOURCE_EXTRACTED_AT": datetime(2026, 7, 25)})
    current, findings = evaluate_history_staleness((history,), set(), date(2026, 7, 29))
    assert current == set() and findings == ()
