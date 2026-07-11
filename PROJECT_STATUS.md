# Project Status

## Project

AI Procurement Copilot

## Edition

Portfolio Edition v1.0

## Current Build

Build 1.0 RC1.2.2 — Export Score Consistency and Scenario Integrity Hotfix

## Current Status

Hotfix implementation completed. GitHub Actions, Streamlit smoke testing, and manual export retest remain pending.

## Canonical Source of Truth

GitHub repository: pratikoperations/AI-Procurement-Copilot

## Release Freeze

Feature development remains frozen. RC1.2.2 addresses validated release defects only.

## RC1.2.2 Scope Completed

- Differentiated RFQ scores from governed Supplier Intelligence scores in readable exports
- Added Supplier 360 Performance, governed Financial, ESG, Innovation, and Supplier 360 fields to readable score reports
- Corrected Freight +50% scenario behavior for delivered-price suppliers
- Preserved zero incremental freight in base-case DDP pricing
- Added embedded freight pass-through only during explicit freight stress
- Standardized scenario terminology to Risk Resilience Score
- Added category-aware TCO headings such as Risk-Adjusted TCO per kg (USD)
- Added regression tests for Raw Material and Packaging freight scenarios

## Validation Status

- Builds 0.1–1.0 RC1.2.1: completed as recorded
- Build 1.0 RC1.2.2: implementation completed
- GitHub Actions: pending
- Streamlit smoke test: pending
- Packaging manual retest: pending
- PET Resin manual retest: pending
- Excel and CSV retest: pending
- Portfolio Edition v1.0 approval: not granted

## Open Release Gates

1. Confirm GitHub Actions are green
2. Confirm live Streamlit deployment loads RC1.2.2
3. Verify Freight +50% increases PET Resin and Packaging unit and annual TCO
4. Verify Supplier Scores Report clearly differentiates RFQ and governed scores
5. Verify scenario sheet uses Risk Resilience Score and category-aware TCO labels
6. Open and inspect all readable and machine-readable downloads
7. Complete or formally waive independent reviews
8. Approve final release-readiness score
9. Create the `v1.0.0` tag only after all gates are complete

## Post-v1.0 Approved Backlog

### Version 1.1 — Time-Aware Procurement Analytics

Documentation-only backlog item. No implementation is authorized during the v1.0 release freeze.

Reference: `docs/FUTURE_TIME_AWARE_ANALYTICS.md`

## Next Milestone

Validate Build 1.0 RC1.2.2. Do not tag v1.0.0 and do not resume feature development.
