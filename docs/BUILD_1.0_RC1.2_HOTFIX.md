# Build 1.0 RC1.2 — Export Integrity and Category-Aware Communication Hotfix

## Purpose

Correct release-blocking defects found during manual review of downloaded reports while preserving the feature freeze.

## Corrective scope

- Added explicit original and normalized currency fields.
- Added auditable FX-rate and comparison-basis fields.
- Corrected synthetic demo currency and unit metadata.
- Added category-aware supplier communication.
- Made supplier communication respect eligibility status.
- Governed recommendation roles using displayed scores and evidence sufficiency.
- Enforced Exit Candidate precedence over Development Candidate.
- Renamed visible risk terminology to Risk Resilience Score.
- Separated business-readable reports from machine-readable audit data.
- Added cross-output consistency tests.

## Release rule

The build remains a release candidate until GitHub Actions, Streamlit smoke testing, and manual opening of all downloadable files are complete.
