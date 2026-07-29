from datetime import date,datetime
from types import SimpleNamespace
from modules.rfq_orchestration import orchestrate_adapter_result


def record(row_id,supplier='S1',material='M1'):
    values={'RFQ_NUMBER':'R1','RFQ_ITEM':'10','SUPPLIER_ID':supplier,'MATERIAL_ID':material,'REQUESTED_QUANTITY':100,'QUOTED_QUANTITY':100,'FULL_QUANTITY_AVAILABLE':True,'BASE_UNIT_PRICE':10,'PRICE_UNIT':1,'QUOTATION_UOM':'EA','COMPARISON_UOM':'EA','CURRENCY':'INR','VALIDITY_END_DATE':date(2026,8,1),'INCOTERMS_CODE':'DAP','LEAD_TIME_DAYS':5,'TECHNICALLY_APPROVED':True,'RISK_SCORE':80,'ESG_SCORE':70,'SOURCE_EXTRACTED_AT':datetime(2026,7,1)}
    return SimpleNamespace(canonical_values=values,provenance=SimpleNamespace(source_row_id=row_id),eligible_for_analysis=True,row_valid=True)


def adapter(quotes,findings=(),metadata=None,history=()):
    return SimpleNamespace(rfq_quotes=tuple(quotes),po_history=tuple(history),findings=tuple(findings),upload_metadata=metadata or {'BASE_CURRENCY':'INR','UPLOAD_CREATED_AT':datetime(2026,7,29)},mode='QUICK_RFQ')


def test_orchestrator_preserves_adapter_result():
    a=adapter([record('Q1'),record('Q2','S2')]); assert orchestrate_adapter_result(a,evaluation_date=date(2026,7,29)).adapter_result is a


def test_adapter_blocker_is_preserved():
    f=SimpleNamespace(severity='Blocking',code='ADAPTER_BLOCK')
    r=orchestrate_adapter_result(adapter([record('Q1')],findings=(f,)),evaluation_date=date(2026,7,29))
    assert r.eligibility_status=='BLOCKED' and 'ADAPTER_BLOCK' in r.blockers


def test_missing_currency_blocks_without_usd_default():
    a=adapter([record('Q1')],metadata={'UPLOAD_CREATED_AT':datetime(2026,7,29)})
    r=orchestrate_adapter_result(a,evaluation_date=date(2026,7,29))
    assert r.comparison_currency is None and r.eligibility_status=='BLOCKED'


def test_expired_record_blocks():
    q=record('Q1'); q.canonical_values['VALIDITY_END_DATE']=date(2026,7,1)
    assert orchestrate_adapter_result(adapter([q]),evaluation_date=date(2026,7,29)).eligibility_status=='BLOCKED'


def test_full_evidence_reaches_gate_with_history():
    h=SimpleNamespace(canonical_values={'MATERIAL_ID':'M1','ORDER_QUANTITY':100,'NET_PRICE':9,'PRICE_UNIT':1,'ORDER_UOM':'EA','COMPARISON_UOM':'EA','CURRENCY':'INR','PO_DATE':date(2026,6,1),'SOURCE_EXTRACTED_AT':datetime(2026,7,1)},provenance=SimpleNamespace(source_row_id='H1'),row_valid=True)
    a=adapter([record('Q1'),record('Q2','S2')],history=(h,)); a.mode='FULL_SOURCING_REVIEW'; a.upload_metadata.update({'HISTORY_START_DATE':date(2026,1,1),'HISTORY_END_DATE':date(2026,7,29),'HISTORY_SOURCE_TRANSACTION':'ME80FN'})
    assert orchestrate_adapter_result(a,evaluation_date=date(2026,7,29)).event_coverage_percent>=70
