# ERP Upload Data Model

## Status

Version 1.1 planning only. This document defines the target data architecture and does not authorize application-code changes.

## Objective

Enable one SAP- or Oracle-derived Excel workbook to feed RFQ analysis, supplier performance, SRM, Supplier 360, TCO, should-cost, risk, contract, and procurement-intelligence modules through a governed canonical data model.

## Workbook Contract

The workbook contains these sheets:

1. `Supplier_Master`
2. `RFQ_Quotes`
3. `Purchase_Orders`
4. `Receipts`
5. `Invoices`
6. `Quality_Performance`
7. `Supplier_Performance`
8. `Contracts`
9. `Material_Master`
10. `Cost_Drivers`

Each sheet must contain:

- `Source_System`
- `Source_Record_ID`
- `Record_Created_Date`
- `Record_Updated_Date`
- `Data_Extraction_Date`

## Canonical Entity Model

### Supplier

Primary key: `Supplier_ID`

Core attributes:

- Supplier name
- Legal entity name
- Country
- Status
- Parent supplier
- Category coverage
- Payment terms
- Currency
- Risk and compliance flags

### Material or Item

Primary key: `Material_ID`

Core attributes:

- Material description
- Category
- Commodity
- Unit of measure
- Specification
- Packaging type or grade

### RFQ Event

Composite business key:

- `RFQ_ID`
- `Supplier_ID`
- `Material_ID`
- `Quote_Line_ID`

### Purchase Order Line

Composite business key:

- `PO_Number`
- `PO_Line_Number`

### Receipt Line

Composite business key:

- `Receipt_Number`
- `Receipt_Line_Number`

### Invoice Line

Composite business key:

- `Invoice_Number`
- `Invoice_Line_Number`

### Contract

Primary key: `Contract_ID`

### Performance Record

Composite business key:

- `Supplier_ID`
- `Performance_Period_Start`
- `Performance_Period_End`
- `Metric_Name`

### Cost Driver

Composite business key:

- `Cost_Driver_ID`
- `Effective_Date`
- `Category`
- `Commodity`

## Standardization Rules

### Supplier ID Matching

Match priority:

1. Exact `Supplier_ID`
2. Exact ERP vendor or supplier number
3. Tax registration or legal identifier
4. Legal entity name plus country
5. Fuzzy name match only with human confirmation

Never silently merge suppliers on name similarity alone.

### Material ID Matching

Match priority:

1. Exact `Material_ID`
2. ERP item or material number
3. Manufacturer part number
4. Specification plus unit plus category
5. Description similarity only with human review

### Currency Normalization

Required fields:

- Original currency
- Original amount
- FX rate used
- FX rate date
- Normalized currency
- Normalized amount

Rules:

- Preserve original values.
- Do not overwrite source currency.
- Reject unsupported or missing currency codes where normalization is mandatory.
- Do not use the current FX rate for historical records without disclosure.

### Unit Normalization

Required fields:

- Original unit
- Conversion factor
- Normalized unit
- Normalized quantity or price

Rules:

- Keep category-aware units such as piece, kg, tonne, litre, metre, or square metre.
- Block comparison where no governed conversion exists.
- Do not convert packaging pieces to weight without explicit pack or specification logic.

### Date Handling

- Store dates internally as ISO `YYYY-MM-DD`.
- Preserve source date text in audit metadata where parsing is ambiguous.
- Reject impossible dates.
- Do not assign missing dates to the extraction date.
- Mark partial periods explicitly.

### Duplicate Handling

- Use declared business keys per sheet.
- Exact duplicate rows may be collapsed only with an audit count.
- Conflicting duplicates must be quarantined.
- Latest-update logic may be used only where `Record_Updated_Date` is trustworthy.

### Missing-Data Governance

Classify every required field as:

- Supplied
- Derived
- Defaulted
- Missing
- Not applicable

Rules:

- Critical missing fields may block recommendation generation.
- Non-critical gaps must lower data confidence.
- Defaulted values must be visible in screens and exports.

### Historical Period Handling

- Preserve all dated transactions and evaluations.
- Distinguish event data from snapshot data.
- Declare one governing date per module.
- Do not mix incomplete and complete periods without warning.
- Show earliest date, latest date, records included, and excluded undated records.

### ERP Custom-Column Mapping

The upload layer must support a configurable mapping table:

| Source Sheet | Source Column | Canonical Column | Transformation | Required | Approved By |
|---|---|---|---|---|---|

Mappings must be saved as profiles, for example:

- `SAP_S4_STANDARD`
- `SAP_ECC_CUSTOM`
- `ORACLE_FUSION_STANDARD`
- `ORACLE_EBS_CUSTOM`

No mapping profile may silently change a business definition.

## Module Consumption

| Canonical dataset | Primary modules |
|---|---|
| Supplier Master | Supplier 360, SRM, risk, qualification |
| RFQ Quotes | RFQ comparison, recommendation, negotiation |
| Purchase Orders | Spend, price history, compliance, TCO |
| Receipts | OTIF, lead time, delivery reliability |
| Invoices | Price variance, payment, freight, tax, leakage |
| Quality Performance | Defects, PPM, rejection, corrective actions |
| Supplier Performance | Scorecards, SRM, trend analytics |
| Contracts | Expiry, compliance, commercial terms |
| Material Master | Category routing, unit governance, specifications |
| Cost Drivers | Should-cost, scenario analysis, negotiation |

## Recommended Ingestion Sequence

1. Validate workbook and sheet names.
2. Load mapping profile.
3. Standardize column names.
4. Validate required fields.
5. Normalize supplier and material identifiers.
6. Parse dates.
7. Normalize currencies and units.
8. Detect duplicates and conflicts.
9. Calculate data-confidence metadata.
10. Route canonical tables to Copilot modules.

## Acceptance Criteria

- All ten sheets are supported.
- Supplier and material matching are auditable.
- Original and normalized values are retained.
- Missing-data status is explicit.
- Historical dates are preserved.
- Duplicate conflicts are quarantined.
- ERP custom mappings are configurable.
- No module receives raw ERP-specific fields directly.
- Human review remains mandatory for ambiguous matches.
