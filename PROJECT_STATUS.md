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

## Executable Evidence
- Python: 3.11.15
- Pinned dependencies: installed successfully
- Compile: VERIFIED COMPLETE
- Full regression: VERIFIED COMPLETE — 162 passed, 0 failed, 0 skipped, 1 warning
- Streamlit startup smoke: VERIFIED COMPLETE
- Existing warning: pandas FutureWarning in `tests/test_adversarial_inputs.py::test_decimal_percentage_is_flagged`

## Maintenance Defect Found and Corrected
The reconstructed maintenance candidate initially failed Supplier Intelligence currency tests because `Risk-Adjusted TCO (USD)` was dropped before being preserved as the canonical USD source. The correction retains the source through a temporary display-only field. No FX formula, ranking, threshold, schema or audit field changed.

## Currency and Selector Status
- Original INR/display inconsistency on main: DEFECT / REGRESSION
- Automated USD/INR/Both and export coverage on candidate: VERIFIED COMPLETE
- Supplier-selector capability: VERIFIED COMPLETE
- Automated selector preservation: VERIFIED COMPLETE
- All-supplier hosted interactive acceptance: NOT STARTED

## Deployment Status
- Historical Streamlit deployment evidence: DOCUMENTED ONLY
- CI/local-equivalent smoke on candidate: VERIFIED COMPLETE
- Current hosted deployment-health claim: REPORTED BUT NOT FOUND
- Authoritative hosted URL: REPORTED BUT NOT FOUND

## Promotion Verdict
**CHANGES REQUIRED**

Required before merge:
1. Directly verify the current hosted application URL and health.
2. Manually exercise every supplier option and confirm the matching Supplier 360 profile.
3. Confirm final PR diff contains no workflow change and final canonical CI remains green.

No Version 1.1 work may begin from this candidate.
