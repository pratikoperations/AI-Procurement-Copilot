# Project Status

## Canonical Baseline
- Repository: `pratikoperations/AI-Procurement-Copilot`
- Stable branch: `main`
- Recovery Build R1 starting SHA: `075fe16d889cdb82b126fe1e07b0c63dca369580`
- Stable release: Portfolio Edition v1.0.0
- Stable status: frozen except approved maintenance

## Exact Development Heads
- `maintenance/v1.0.1`: `ba49af44d8c1ff36d9d5d612e0909f5698d1d433`
- `v1.1-development`: `0c2281e47ff4e2b4b8153fbde6350d5c9c1a4341`

## Recovery Build R1
- Branch: `recovery/r1-v1.0.1-baseline-verification`
- Draft PR: #9
- Reconciliation approach: reconstruct validated maintenance files from current main
- Version 1.1 implementation: OUT OF SCOPE

## Standalone Main Evidence
- Python: 3.11.15
- Dependencies: installed successfully
- Compile: VERIFIED COMPLETE
- Full regression: VERIFIED COMPLETE — 114 passed, 0 failed, 0 skipped, 1 warning
- Streamlit startup smoke: VERIFIED COMPLETE

## Candidate Evidence
- Python: 3.11.15
- Compile: VERIFIED COMPLETE
- Focused maintenance tests: VERIFIED COMPLETE
- Full regression: VERIFIED COMPLETE — 162 passed, 0 failed, 0 skipped, 1 warning
- Streamlit startup smoke: VERIFIED COMPLETE
- Final workflow file diff: absent

## Maintenance Defect Corrected
The candidate initially lost `Risk-Adjusted TCO (USD)` before display reconstruction. The correction preserves the canonical source through a temporary display-only field. No FX formula, ranking, threshold, schema, recommendation or audit field changed.

## Hosted Acceptance
- Candidate URL: `https://ai-procurement-copilot-pr9.streamlit.app/`
- Candidate branch and Python startup evidence: VERIFIED COMPLETE
- Current hosted deployment health: VERIFIED COMPLETE
- All six supplier selections and matching Supplier 360 profiles: VERIFIED COMPLETE
- Hosted USD/INR/Both visual acceptance: VERIFIED COMPLETE
- Evidence boundary: hosted functional acceptance was manually performed and confirmed by the project owner.

## Promotion Verdict
**MERGE READY**

All Recovery R1 acceptance gates are closed. PR #9 remains draft and unmerged pending final owner review and explicit merge authorization.

No Version 1.1 work may begin from this candidate until separately authorized.
