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
| `maintenance/v1.0.1` | `ba49af44d8c1ff36d9d5d612e0909f5698d1d433` | VERIFIED COMPLETE |
| `v1.1-development` | `0c2281e47ff4e2b4b8153fbde6350d5c9c1a4341` | VERIFIED PARTIAL |
| `recovery/r1-v1.0.1-baseline-verification` | final SHA recorded in PR metadata | VERIFIED PARTIAL pending hosted acceptance |

These are direct branch/ref resolutions. PR merge SHAs, synthetic merge commits and merge-base SHAs were not substituted.

## Recovery R1 Findings
- Fourteen maintenance code/test files were reconstructed from current canonical main.
- Initial regression exposed loss of the canonical `Risk-Adjusted TCO (USD)` source during display rebuilding.
- The source is now preserved through a temporary display-only field before USD/INR/Both outputs are rebuilt.
- No FX formula, ranking, threshold, schema, recommendation or award-control rule changed.
- Exact main standalone evidence: Python 3.11.15; compile PASS; `114 passed, 0 failed, 0 skipped, 1 warning`; Streamlit smoke PASS.
- Candidate evidence: Python 3.11.15; compile PASS; `162 passed, 0 failed, 0 skipped, 1 warning`; Streamlit smoke PASS.
- Final PR diff contains no workflow file and no Version 1.1 or ERP feature file.

## Claim and Capability Status
| Item | Classification |
|---|---|
| Portfolio Edition v1.0.0 standalone executable baseline | VERIFIED COMPLETE |
| Missing supplier-selector claim | REPORTED BUT NOT FOUND |
| Supplier-selector capability | VERIFIED COMPLETE |
| Automated selector preservation | VERIFIED COMPLETE |
| Hosted all-supplier interactive acceptance | NOT STARTED |
| INR issue on original main | DEFECT / REGRESSION |
| Reconstructed INR/currency candidate automated evidence | VERIFIED COMPLETE |
| Historical deployment acceptance | DOCUMENTED ONLY |
| Current hosted deployment healthy | REPORTED BUT NOT FOUND |
| Authoritative hosted URL | REPORTED BUT NOT FOUND |
| Hosted USD/INR/Both visual acceptance | NOT STARTED |
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
Reconstruction from canonical main remains the selected approach. Promotion verdict: **CHANGES REQUIRED** because direct hosted deployment, supplier-by-supplier interaction and hosted currency-mode acceptance remain unverified.

Version 1.1 feature implementation remains OUT OF SCOPE.
