from decimal import Decimal
from modules.rfq_evidence_coverage import quotation_coverage,aggregate_item,aggregate_event


def complete():
    return {'REQUESTED_QUANTITY':100,'QUOTED_QUANTITY':100,'FULL_QUANTITY_AVAILABLE':True,'INCOTERMS_CODE':'DAP','LEAD_TIME_DAYS':10,'TECHNICALLY_APPROVED':True,'RISK_SCORE':80,'ESG_SCORE':70}


def test_full_coverage_is_100():
    assert quotation_coverage(complete(),{'NORMALIZED_UNIT_PRICE':Decimal('10')},has_history_match=True).coverage_percent==Decimal('100')


def test_missing_evidence_gets_zero_not_partial():
    assert quotation_coverage({}, {}, has_history_match=False).coverage_percent==0


def test_item_uses_minimum_supplier_coverage():
    a=quotation_coverage(complete(),{'NORMALIZED_UNIT_PRICE':1},has_history_match=True)
    b=quotation_coverage({'REQUESTED_QUANTITY':100,'QUOTED_QUANTITY':100},{'NORMALIZED_UNIT_PRICE':1},has_history_match=False)
    assert aggregate_item([a,b]).coverage_percent==b.coverage_percent


def test_event_quantity_weighted():
    a=quotation_coverage(complete(),{'NORMALIZED_UNIT_PRICE':1},has_history_match=True); b=quotation_coverage({}, {}, has_history_match=False)
    score,method=aggregate_event({'A':a,'B':b},{'A':100,'B':300})
    assert method=='REQUESTED_QUANTITY_WEIGHTED' and score==Decimal('25')


def test_event_equal_fallback_disclosed():
    a=quotation_coverage(complete(),{'NORMALIZED_UNIT_PRICE':1},has_history_match=True)
    assert aggregate_event({'A':a},{'A':None})[1]=='EQUAL_ITEM_WEIGHTED_FALLBACK'
