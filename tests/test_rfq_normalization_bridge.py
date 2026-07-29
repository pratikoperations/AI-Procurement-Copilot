from datetime import date
from decimal import Decimal
from modules.rfq_normalization_bridge import normalize_record


def test_same_basis_preserves_source():
    r=normalize_record({'QUOTED_QUANTITY':10,'BASE_UNIT_PRICE':100,'PRICE_UNIT':1,'QUOTATION_UOM':'EA','COMPARISON_UOM':'EA','CURRENCY':'INR'},comparison_currency='INR',quantity_field='QUOTED_QUANTITY',uom_field='QUOTATION_UOM',price_field='BASE_UNIT_PRICE')
    assert r.status=='NORMALIZED' and r.normalized_values['NORMALIZED_UNIT_PRICE']==Decimal('100')


def test_uom_quantity_multiplies_price_divides():
    r=normalize_record({'QUOTED_QUANTITY':10,'BASE_UNIT_PRICE':1000,'PRICE_UNIT':1,'QUOTATION_UOM':'BOX','COMPARISON_UOM':'EA','UOM_CONVERSION_FACTOR':100,'CURRENCY':'INR'},comparison_currency='INR',quantity_field='QUOTED_QUANTITY',uom_field='QUOTATION_UOM',price_field='BASE_UNIT_PRICE')
    assert r.normalized_values['NORMALIZED_QUANTITY']==Decimal('1000') and r.normalized_values['NORMALIZED_UNIT_PRICE']==Decimal('10')


def test_fx_divides_source_currency_per_target():
    r=normalize_record({'QUOTED_QUANTITY':1,'BASE_UNIT_PRICE':8300,'PRICE_UNIT':1,'QUOTATION_UOM':'EA','COMPARISON_UOM':'EA','CURRENCY':'INR','EXCHANGE_RATE':83,'EXCHANGE_RATE_DATE':date(2026,7,1)},comparison_currency='USD',quantity_field='QUOTED_QUANTITY',uom_field='QUOTATION_UOM',price_field='BASE_UNIT_PRICE')
    assert r.normalized_values['NORMALIZED_UNIT_PRICE']==Decimal('100')


def test_missing_fx_blocks():
    r=normalize_record({'QUOTED_QUANTITY':1,'BASE_UNIT_PRICE':10,'PRICE_UNIT':1,'QUOTATION_UOM':'EA','COMPARISON_UOM':'EA','CURRENCY':'EUR'},comparison_currency='INR',quantity_field='QUOTED_QUANTITY',uom_field='QUOTATION_UOM',price_field='BASE_UNIT_PRICE')
    assert 'FX_RATE_AND_DATE_REQUIRED' in r.blockers


def test_no_silent_currency_default():
    r=normalize_record({'QUOTED_QUANTITY':1,'BASE_UNIT_PRICE':10,'PRICE_UNIT':1,'QUOTATION_UOM':'EA','COMPARISON_UOM':'EA','CURRENCY':'INR'},comparison_currency=None,quantity_field='QUOTED_QUANTITY',uom_field='QUOTATION_UOM',price_field='BASE_UNIT_PRICE')
    assert 'COMPARISON_CURRENCY_REQUIRED' in r.blockers
