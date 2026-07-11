# ERP Adversarial Dataset Specification

## Status
Planning only. No application code or Version 1.0 changes.

## Purpose
Define a deliberately poor-quality workbook that proves the ERP upload workflow fails safely, explains defects clearly, and never produces unsupported procurement recommendations.

## Workbook
File name: `erp_adversarial_procurement_workbook.xlsx`

Use the same seven priority sheets as the MVP.

## Structural Defects
Include:
- Missing required sheet
- Extra unsupported sheet
- Empty required sheet
- Duplicate header names
- Blank header
- Hidden columns
- merged cells
- macro-enabled file variant for rejection
- formula cells in identifier and price columns
- corrupted workbook copy

## Identifier Defects
Include:
- Missing Supplier_ID
- Missing Material_ID
- leading zeros lost
- duplicate Source_Record_ID
- supplier transaction not found in Supplier_Master
- material transaction not found in Material_Master
- conflicting supplier legal names
- one supplier ID assigned to two legal entities

## Currency Defects
Include:
- Blank currency
- invalid code such as `USX`
- mixed currencies without FX data
- normalized value inconsistent with FX rate
- historical transaction using future FX date
- currency stored in amount field

## Unit Defects
Include:
- Unknown UOM
- incompatible units across bids
- zero conversion factor
- negative conversion factor
- piece-to-kg conversion without weight basis
- price-per-tonne labelled price-per-kg

## Numeric Defects
Include:
- Negative price
- zero quoted quantity
- negative quantity
- percentages above 100
- percentages below 0
- rejected quantity above received quantity
- nonnumeric text in numeric field
- extreme outlier price

## Date Defects
Include:
- Impossible date
- mixed date formats
- receipt before PO date
- performance end before start
- quote expiry before effective date
- future extraction date
- missing governing date
- partial period without status

## Duplicate and Conflict Defects
Include:
- Exact duplicate rows
- conflicting duplicate PO lines
- duplicate RFQ quote with different price
- duplicate supplier records with different country
- multiple latest records with same update timestamp

## Business Rule Defects
Include:
- Blocked supplier in RFQ
- inactive material in current PO
- expired quote treated as current
- supplier performance score without period
- cost driver without source or effective date
- DDP price plus duplicated full freight
- unsupported category and commodity

## Security Defects
Include spreadsheet cells beginning with:
- `=`
- `+`
- `-`
- `@`

These must be treated as untrusted data and never executed.

## Expected Severity Outcomes
- Structural corruption: BLOCKING
- Missing critical identifiers: BLOCKING
- Unsupported currency or incompatible UOM: BLOCKING for affected module
- Ambiguous entity match: REVIEW REQUIRED
- Missing optional commercial term: WARNING
- Exact duplicate: WARNING or INFO after auditable collapse
- Conflicting duplicate: BLOCKING or quarantine

## Expected System Behaviour
- Workbook-level blockers prevent processing.
- Row-level blockers quarantine affected rows.
- No silent correction of critical fields.
- No fuzzy supplier merge without approval.
- Accepted, warned, quarantined, and rejected counts are shown.
- A downloadable defect report is produced.
- Downstream module eligibility is explicit.

## Acceptance Criteria
- Every listed defect exists in at least one test case.
- Expected severity is documented.
- No blocked dataset produces a final award recommendation.
- Original defective values remain available in audit output.
