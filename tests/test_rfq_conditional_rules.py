from datetime import date, datetime
from types import SimpleNamespace
from modules.rfq_conditional_rules import resolve_evaluation_date,evaluate_conditional_rules


def rec(row_id,values,eligible=True):
    return SimpleNamespace(canonical_values=values,provenance=SimpleNamespace(source_row_id=row_id),eligible_for_analysis=eligible,row_valid=eligible)


def result(mode='QUICK_RFQ',metadata=None,quotes=(),history=()):
    return SimpleNamespace(mode=mode,upload_metadata=metadata,rfq_quotes=quotes,po_history=history)


def test_evaluation_date_precedence():
    r=result(metadata={'UPLOAD_CREATED_AT':datetime(2026,7,2),'EXTRACTED_AT':datetime(2026,7,1)})
    assert resolve_evaluation_date(r.upload_metadata,(),date(2026,7,3))[1]=='EXPLICIT_INPUT'
    assert resolve_evaluation_date(r.upload_metadata,())[1]=='UPLOAD_CREATED_AT'


def test_system_date_warns():
    _,source,findings=resolve_evaluation_date({},(),today=date(2026,7,29))
    assert source=='SYSTEM_DATE' and findings[0].code=='SYSTEM_DATE_FALLBACK'


def test_expired_quote_is_ineligible():
    q=rec('Q1',{'MATERIAL_ID':'M1','VALIDITY_END_DATE':date(2026,7,1)})
    flags,_,findings=evaluate_conditional_rules(result(quotes=(q,)),date(2026,7,29))
    assert not flags['Q1'] and any(f.code=='QUOTATION_EXPIRED' for f in findings)


def test_material_id_requires_approval():
    q=rec('Q1',{'VALIDITY_END_DATE':date(2026,8,1)})
    flags,_,_=evaluate_conditional_rules(result(quotes=(q,)),date(2026,7,29))
    assert not flags['Q1']
    flags,_,_=evaluate_conditional_rules(result(quotes=(q,)),date(2026,7,29),approved_free_text_row_ids={'Q1'})
    assert flags['Q1']


def test_full_review_requires_metadata():
    _,_,findings=evaluate_conditional_rules(result(mode='FULL_SOURCING_REVIEW'),date(2026,7,29))
    assert sum(f.code=='FULL_REVIEW_HISTORY_METADATA_REQUIRED' for f in findings)==3
