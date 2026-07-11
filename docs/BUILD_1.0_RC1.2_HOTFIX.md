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

## Regression failure investigation

The first RC1.2 quality-check runs failed in `tests/test_download_consistency.py::test_blocked_memo_withholds_award_language`.

### Root cause

`generate_executive_memo()` used:

```python
eligibility.get("status", award_status(recommended, confidence))
```

Python evaluates function arguments before calling `dict.get()`. Therefore `award_status()` executed even when `eligibility["status"]` already contained `Blocked`. The blocked-path test intentionally used a minimal supplier record without `total_score`, causing a `KeyError` before the governed blocked memo could be produced.

### Fix

The fallback is now evaluated lazily:

```python
status = eligibility.get("status")
if not status:
    status = award_status(recommended, confidence)
```

This preserves the eligibility decision and avoids unnecessary access to award-scoring fields when the recommendation is already blocked.

## Validation result

A controlled pull-request workflow verification completed successfully:

- Python compilation: Passed
- Complete regression suite: Passed
- Streamlit smoke test: Passed
- No additional failures introduced

Temporary diagnostic pull requests were closed without merging and did not alter application logic on `main`.

## Release rule

The code-level RC1.2 regression gate is clear. The build remains a release candidate until live Streamlit validation and manual opening of all downloadable files are complete.
