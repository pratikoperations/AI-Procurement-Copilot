# Synthetic Oracle ERP Workbook Specification

## Status
Planning only. No application code or Version 1.0 changes.

## Purpose
Define a realistic Oracle-style procurement workbook that proves the ingestion layer is profile-driven rather than hard-coded to SAP field names.

## Workbook
File name: `synthetic_oracle_procurement_workbook.xlsx`

Required sheets:
1. `Supplier_Master`
2. `RFQ_Quotes`
3. `Purchase_Orders`
4. `Receipts`
5. `Supplier_Performance`
6. `Material_Master`
7. `Cost_Drivers`

## Data Scale
Match the SAP synthetic workbook closely enough to support like-for-like tests:
- Suppliers: 20–30
- Materials: 30–50
- RFQ rows: 150–250
- PO rows: 300–500
- Receipt rows: 300–500
- Performance rows: 80–120
- Cost drivers: 60–100
- Historical period: 18 months

## Oracle-Style Source Conventions
Use source headers such as:
- `SUPPLIER_ID`
- `SUPPLIER_NAME`
- `COUNTRY_CODE`
- `ITEM_ID`
- `ITEM_NUMBER`
- `DESCRIPTION`
- `PO_HEADER_ID`
- `PO_LINE_ID`
- `LINE_NUM`
- `CREATION_DATE`
- `UNIT_PRICE`
- `CURRENCY_CODE`
- `UOM_CODE`
- `QUANTITY`
- `BUSINESS_UNIT`
- `NEED_BY_DATE`
- `RECEIPT_DATE`
- `TERMS_NAME`
- `FOB_LOOKUP_CODE`

## Required Differences from SAP Dataset
- Oracle-style numeric and text identifiers
- Different source column names
- Different purchasing organization terminology
- Different item numbering conventions
- Different date-field labels
- Different supplier status labels
- Equivalent business scenarios to support mapping equivalence tests

## Sheet Scenarios

### Supplier_Master
Include active, inactive, parent/child, duplicate-name, and renamed suppliers.

### RFQ_Quotes
Include multi-supplier negotiations, mixed currencies, quote validity, MOQ, lead time, freight, payment terms, and incomplete rows.

### Purchase_Orders
Include contract-linked and standalone POs, multiple business units, price movements, and split awards.

### Receipts
Include on-time, late, partial, rejected, and over-delivered receipts.

### Supplier_Performance
Include periodic OTIF, quality, service, responsiveness, and overall-score records.

### Material_Master
Include packaging and raw-material items with multiple UOMs, grades, specifications, and active statuses.

### Cost_Drivers
Include commodity, freight, labour, energy, scrap, conversion, overhead, and margin drivers.

## Embedded Edge Cases
- Supplier IDs stored as text and numbers
- Duplicate supplier names
- One missing material reference
- One incompatible UOM
- One unsupported currency code
- One invalid date
- One duplicate PO line
- One ambiguous parent supplier
- One performance period with end date before start date

## Expected Outcomes
- Valid Oracle rows map to the same canonical schema as SAP rows.
- Equivalent SAP and Oracle business cases produce equivalent canonical outputs.
- Mapping differences remain visible in the audit report.
- Ambiguous and invalid records are reviewed or blocked.

## Acceptance Criteria
- All seven sheets present
- Oracle-style headers used
- At least 18 months of dated data
- Equivalent scenarios to SAP dataset
- Mapping profile required for successful ingestion
- No real or confidential data included
