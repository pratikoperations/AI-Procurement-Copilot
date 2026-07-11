# External File Validation Report

## Scope

Build 0.9.6 includes synthetic and anonymized CSV test files representing common supplier-file conditions. No confidential supplier information is committed.

## Dataset coverage

### Packaging

- Standard canonical file
- Alternate headers
- Missing optional fields
- Invalid numeric and percentage values

### Raw material

- Standard resin file
- Alternate metal headers
- Mixed currencies
- Missing required fields

### Edge cases

- Duplicate suppliers
- Decimal and whole-number percentages
- Negative values
- Capacity shortfall
- Single supplier
- Fifty-supplier file

## Automated checks

- CSV ingestion
- Header normalization
- Canonical required fields
- Duplicate warnings
- Negative-value rejection
- Mixed-currency blocking
- Capacity-shortfall detection
- Large-file row preservation
- Quality-score and validation behavior

## Current findings

1. Files with alternate headers require visible mapping review.
2. Missing optional data can still support analysis but should reduce confidence.
3. Mixed currency and mixed UOM comparisons must remain blocked until normalized.
4. Negative commercial or operational values must block calculation.
5. Decimal percentages such as 0.95 require source-format confirmation.
6. Capacity must be validated against annual demand and recommended allocation.

## Limitations

- Current test assets are CSV; multi-sheet and merged-cell XLSX testing remains a manual release task.
- Files are synthetic, not extracted from an operating ERP or supplier portal.
- Hidden columns, workbook formulas and date-format variations require additional production-level testing.
- Large-file coverage is currently 50 suppliers; scale beyond that is not certified.

## Status

- Test files: Created
- Automated file tests: Added
- GitHub Actions: Pending latest run
- Manual uploaded-file validation in deployed Streamlit: Pending
- Real anonymized user RFQ validation: Pending
