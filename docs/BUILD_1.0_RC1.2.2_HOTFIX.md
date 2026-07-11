# Build 1.0 RC1.2.2 — Export Score Consistency and Scenario Integrity Hotfix

## Purpose

Close release-blocking manual-validation findings without adding features or changing scoring philosophy.

## Defects addressed

### RC1-DEF-012 — Readable score inconsistency

Readable Supplier Scores used RFQ-engine performance and ESG scores while Supplier Comparison and the executive narrative used governed Supplier Intelligence scores. Because the same labels were used for different measures, the workbook appeared contradictory.

### Resolution

Readable score exports now distinguish:

- RFQ Performance Score
- RFQ ESG Score
- Supplier 360 Performance Score
- Governed Financial Indicator
- Governed ESG Maturity Score
- Governed Innovation Maturity Score
- Supplier 360 Score

Raw RFQ scores remain unchanged for auditability. Governed Supplier Intelligence scores are exposed to readable exports with explicit business labels.

### RC1-DEF-013 — Freight scenario did not change winning TCO

The winning PET Resin supplier used DDP terms. The TCO engine correctly treated base-case incremental buyer freight as zero, but the stress scenario also remained zero because DDP freight exposure was not stressed. This made Freight +50% identical to Base Case.

### Resolution

A governed embedded-freight pass-through rule now applies only when an explicit freight shock is selected:

- Base-case DDP incremental freight remains zero.
- During a freight shock, a transparent embedded freight share is stressed to reflect supplier pass-through exposure.
- Non-DDP terms continue to use their existing direct freight exposure factors.

The same controlled logic is used for Packaging and Raw Material TCO engines.

### RC1-DEF-014 — Ambiguous scenario terminology

Readable scenario exports still used Risk Score and Advanced TCO Unit USD.

### Resolution

Readable scenario headings now use:

- Risk Resilience Score
- Risk-Adjusted TCO per category unit (USD)
- Annual TCO (USD)

For PET Resin the heading is Risk-Adjusted TCO per kg (USD).

## Files changed

- `modules/tco.py`
- `modules/raw_material_tco.py`
- `modules/scenario.py`
- `modules/supplier_comparison.py`
- `modules/exports.py`
- `modules/config.py`
- `tests/test_export_integrity.py`
- `tests/test_scenario_export_integrity.py`

## Validation coverage

Tests verify:

- RFQ and governed Supplier Intelligence scores are explicitly differentiated.
- Governed score values remain available in readable exports.
- Freight +50% increases Raw Material unit and annual TCO.
- Freight +50% increases Packaging unit and annual TCO.
- Readable scenario exports use Risk Resilience Score.
- Category-aware TCO headings use the correct unit.

## Release boundary

- No new feature was introduced.
- No score weighting or recommendation philosophy changed.
- Raw audit outputs remain available.
- Version 1.0 release freeze remains active.
- Manual retesting and green CI are required before release approval.
