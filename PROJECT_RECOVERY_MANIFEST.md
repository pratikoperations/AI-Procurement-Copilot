# Project Recovery Manifest

## Repository Identity
- Repository: `pratikoperations/AI-Procurement-Copilot`
- Canonical source of truth: GitHub
- Canonical stable branch: `main`
- Recovery-governance main baseline: `075fe16d889cdb82b126fe1e07b0c63dca369580`
- Stable release: Portfolio Edition v1.0.0, frozen except approved maintenance
- Recovery date: 2026-07-15

## Approved Classification Taxonomy
Every formal status uses exactly one of: VERIFIED COMPLETE, VERIFIED PARTIAL, IMPLEMENTED BUT UNTESTED, DOCUMENTED ONLY, REPORTED BUT NOT FOUND, NOT STARTED, DEFECT / REGRESSION, DEFERRED, OUT OF SCOPE.

## Exact Branch Baselines
| Branch | Exact HEAD | Classification |
|---|---|---|
| `main` at R1 start | `075fe16d889cdb82b126fe1e07b0c63dca369580` | VERIFIED COMPLETE |
| `maintenance/v1.0.1` | `ba49af44d8c1ff36d9d5d612e0909f5698d1d433` | VERIFIED COMPLETE for HEAD capture |
| `v1.1-development` | `0c2281e47ff4e2b4b8153fbde6350d5c9c1a4341` | VERIFIED PARTIAL for ERP foundation |
| `recovery/r1-v1.0.1-baseline-verification` | final SHA recorded in PR metadata | VERIFIED PARTIAL pending acceptance |

These are branch-ref resolutions. PR merge SHAs, synthetic merge commits and merge-base SHAs were not substituted.

## Recovery R1 Findings
- The historical maintenance line diverged from current main.
- Fourteen maintenance code/test files were reconstructed on current main to preserve recovery-governance and portability controls.
- Initial reconstructed regression failed in `tests/test_supplier_intelligence_currency.py`.
- Root cause: the display wrapper dropped `Risk-Adjusted TCO (USD)` before preserving it as a canonical USD source.
- Correction preserves that source in a temporary display-only field before rebuilding USD/INR/Both columns.
- No FX formula, ranking, threshold, schema, award-control rule or Version 1.1 capability changed.
- Final evidence: Python 3.11.15; dependencies installed; compile PASS; `162 passed, 0 failed, 0 skipped, 1 warning`; Streamlit smoke PASS.

## Claim and Capability Status
| Item | Classification |
|---|---|
| Portfolio Edition v1.0.0 baseline | VERIFIED COMPLETE |
| Missing supplier-selector claim | REPORTED BUT NOT FOUND |
| Supplier-selector capability | VERIFIED COMPLETE |
| Automated selector preservation | VERIFIED COMPLETE |
| Hosted all-supplier interactive acceptance | NOT STARTED |
| INR issue on original main | DEFECT / REGRESSION |
| Reconstructed INR/currency candidate | VERIFIED COMPLETE for automated evidence |
| Historical deployment acceptance | DOCUMENTED ONLY |
| Current hosted deployment healthy | REPORTED BUT NOT FOUND |
| v1.1 branch existence | VERIFIED COMPLETE |
| v1.1 ERP foundation | VERIFIED PARTIAL |
| Complete ERP pipeline/report/UI claims | REPORTED BUT NOT FOUND |

## Evidence Records
- `RECOVERY_R1_BASELINE_VERIFICATION.md`
- `RECOVERY_R1_MAIN_TEST_EVIDENCE.md`
- `RECOVERY_R1_MAINTENANCE_TEST_EVIDENCE.md`
- `RECOVERY_R1_CURRENCY_VALIDATION_MATRIX.md`
- `RECOVERY_R1_SUPPLIER_SELECTOR_VALIDATION.md`
- `RECOVERY_R1_DEPLOYMENT_EVIDENCE.md`
- `RECOVERY_R1_MAINTENANCE_RECONCILIATION_PLAN.md`

## Recovery R1 Decision
Reconstruction from canonical main is the selected approach. Promotion verdict: **CHANGES REQUIRED** until current hosted runtime and all-supplier interactive acceptance are directly evidenced and final PR review confirms no workflow diff.

Version 1.1 feature implementation remains OUT OF SCOPE.
