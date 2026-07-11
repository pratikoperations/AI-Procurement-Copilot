# Synthetic SAP ERP Workbook Specification

## Status
Planning only. No application code or Version 1.0 changes.

## Purpose
Define a realistic SAP-style procurement workbook for development, mapping, validation, and regression testing of the ERP upload MVP.

## Workbook
File name: `synthetic_sap_procurement_workbook.xlsx`

Required sheets:
1. `Supplier_Master`
2. `RFQ_Quotes`
3. `Purchase_Orders`
4. `Receipts`
5. `Supplier_Performance`
6. `Material_Master`
7. `Cost_Drivers`

## Data Scale
- Suppliers: 20–30
- Materials: 30–50
- RFQ rows: 150–250
- PO rows: 300–500
- Receipt rows: 300–500
- Supplier performance rows: 80–120
- Cost driver rows: 60–100
- Historical period: 18 months

## SAP-Style Source Conventions
Use source headers such as:
- `LIFNR`
- `NAME1`
- `LAND1`
- `MATNR`
- `MAKTX`
- `MEINS`
- `EBELN`
- `EBELP`
- `BEDAT`
- `NETPR`
- `WAERS`
- `MENGE`
- `WERKS`
- `EINDT`
- `BUDAT`
- `ZTERM`
- `INCO1`

The workbook must remain synthetic and must not reproduce any confidential organization data.

## Sheet Scenarios

### Supplier_Master
Include:
- Active suppliers
- Blocked suppliers
- Duplicate supplier names with different IDs
- Parent/child suppliers
- Multiple countries
- Missing payment terms in selected rows
- Supplier name abbreviations

### RFQ_Quotes
Include:
- Multiple suppliers per RFQ
- Multiple currencies
- Multiple units
- DDP, FOB, EXW, and CIF terms
- Valid and expired quotes
- Missing lead time in selected rows
- MOQ differences
- Freight included and excluded cases

### Purchase_Orders
Include:
- Multiple plants
- Contract and non-contract orders
- Price changes over time
- Split awards
- Open and closed POs
- Partial releases

### Receipts
Include:
- On-time receipts
- Late receipts
- Early receipts
- Partial receipts
- Over-deliveries
- Rejected quantities
- Receipt before promised date

### Supplier_Performance
Include:
- Quarterly records
- OTIF, quality, service, and responsiveness scores
- Missing metrics
- Improving and declining suppliers
- Snapshot and historical records

### Material_Master
Include:
- Packaging and raw-material items
- Active and obsolete materials
- kg, piece, tonne, litre, metre, and square-metre units
- material groups
- grades and specifications
- standard cost examples

### Cost_Drivers
Include:
- Commodity indices
- freight rates
- labour rates
- energy rates
- scrap assumptions
- conversion cost
- overhead
- supplier margin
- ERP, manual, and external source types

## Embedded Edge Cases
Include at least:
- Leading-zero supplier IDs
- Leading-zero material IDs
- Unknown unit requiring mapping
- Missing currency in one noncritical sample row
- Duplicate source record ID
- Conflicting duplicate PO line
- Invalid date string
- Inactive supplier with active RFQ
- Obsolete material in historical PO
- supplier renamed during period

## Expected Outcomes
- Core valid rows should map successfully.
- Ambiguous supplier names should require review.
- Unknown units should block affected comparisons.
- Duplicate conflicts should be quarantined.
- Historical coverage should be visible.
- No unsafe recommendation should run on blocked data.

## Acceptance Criteria
- All seven sheets present
- SAP-style source headers used
- At least 18 months of dated data
- Edge cases documented
- Canonical mapping possible through profile rules
- No real or confidential data included
