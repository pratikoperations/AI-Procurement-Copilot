# Project Status

## Project

AI Procurement Copilot

## Edition

Portfolio Edition v1.0

## Current Build

Build 1.0 RC1.2.3 — Scenario Engine Column Alignment Critical Hotfix

## Current Status

Critical runtime hotfix implementation completed. GitHub Actions, Streamlit smoke testing, and live scenario retest remain pending.

## Canonical Source of Truth

GitHub repository: pratikoperations/AI-Procurement-Copilot

## Release Freeze

Feature development remains frozen. RC1.2.3 addresses only the validated scenario-rendering defect.

## RC1.2.3 Scope Completed

- Aligned the dashboard scenario renderer with the governed RC1.2.2 scenario schema
- Added a reusable column resolver instead of directly hard-coding one annual-TCO heading
- Preferred `Annual TCO (USD)` while retaining backward compatibility with `Annual TCO USD` and `annual_tco_usd`
- Updated INR conversion and Plotly chart logic to use the resolved annual-TCO column
- Preserved category-aware TCO labels for kg and piece
- Preserved RC1.2.2 freight scenario calculations
- Added Packaging and Raw Material scenario-schema regression tests

## Validation Status

- Builds 0.1–1.0 RC1.2.2: completed as recorded
- Build 1.0 RC1.2.3: implementation completed
- GitHub Actions: pending
- Streamlit smoke test: pending
- PET Resin Multi-Scenario Stress Test retest: pending
- Packaging Multi-Scenario Stress Test retest: pending
- Excel and CSV retest: pending
- Portfolio Edition v1.0 approval: not granted

## Open Release Gates

1. Confirm the latest GitHub Actions workflow is green
2. Confirm the live Streamlit deployment loads Build 1.0 RC1.2.3
3. Confirm Raw Material Multi-Scenario Stress Test renders without `KeyError`
4. Confirm Packaging Multi-Scenario Stress Test renders without `KeyError`
5. Verify Freight +50% increases PET Resin and Packaging unit and annual TCO
6. Verify Supplier Scores Report clearly differentiates RFQ and governed scores
7. Verify scenario sheet uses Risk Resilience Score and category-aware TCO labels
8. Open and inspect all readable and machine-readable downloads
9. Complete or formally waive independent reviews
10. Approve final release-readiness score
11. Create the `v1.0.0` tag only after all gates are complete

## Post-v1.0 Approved Backlog

### Version 1.1 — Time-Aware Procurement Analytics

Documentation-only backlog item. No implementation is authorized during the v1.0 release freeze.

Reference: `docs/FUTURE_TIME_AWARE_ANALYTICS.md`

## Next Milestone

Validate Build 1.0 RC1.2.3. Do not tag v1.0.0 and do not resume feature development.
