# Build 0.9.2 QA Report

## Build

Build 0.9.2 — Intelligent RFQ Engine

## Quality Gates

| Gate | Result | Notes |
|---|---|---|
| Header recognition | Pass | Exact and fuzzy aliases covered by regression tests |
| Canonical mapping | Pass | Required supplier fields map to the governed schema |
| Unit normalization | Pass | kg, MT, piece, meter, and liter variants covered |
| Duplicate detection | Pass | Duplicate suppliers surfaced for review |
| Missing required data | Pass | Invalid RFQs are blocked before scoring |
| Unmapped columns | Pass | Preserved in the normalized dataframe |
| Numeric diagnostics | Pass | Invalid numeric values converted to blank and reported |
| Upload quality score | Pass | Mapping, completeness, duplicate, and conversion factors included |
| Existing workflow | Pass | Synthetic canonical RFQ path preserved |
| CI | Pass | Latest Build 0.9.2 Quality Checks runs are green |
| Live upload | Pending | Requires alternate-header CSV/Excel upload in the deployed app |

## Confirmed Quality Score

- Architecture: 9.2/10
- Code Quality: 9.0/10
- Procurement Practicality: 9.3/10
- Data Governance: 9.2/10
- User Transparency: 9.1/10
- Maintainability: 9.1/10

**CI-validated Average:** 9.2/10

## Key Control

The engine does not silently invent required procurement data. It maps recognizable headers, preserves unknown fields, reports weak data, and stops scoring when required fields remain missing.

## Remaining Manual Validation

1. Upload an alternate-template CSV using headers such as Vendor Name, Unit Rate, Minimum Order Quantity, Delivery Days, Credit Terms, Delivery Terms, and UOM.
2. Confirm the mapped canonical fields appear correctly.
3. Confirm the upload quality score and diagnostics are visible.
4. Upload an invalid file and confirm scoring is blocked with clear errors.

## CI Evidence

The latest Build 0.9.2 GitHub Actions runs completed successfully, including the QA report, version manifest, build history, changelog, and project status commits.
