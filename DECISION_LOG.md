# Decision Log

## Preserved Governance Decisions
- GitHub is the canonical source of truth.
- Portfolio Edition v1.0.0 remains frozen except approved maintenance.
- Award logic remains deterministic, auditable and human-controlled.
- Version 1.1 is real but partial; ERP feature work remains separately governed.
- Unsupported completion claims remain REPORTED BUT NOT FOUND.
- Supplier-selector capability is VERIFIED COMPLETE; the missing-selector claim is REPORTED BUT NOT FOUND.
- Historical deployment evidence is DOCUMENTED ONLY; current hosted health requires direct evidence.

## DEC-R1-001 — Exact Branch Baselines
- Date: 2026-07-15
- Main: `075fe16d889cdb82b126fe1e07b0c63dca369580`
- Maintenance: `ba49af44d8c1ff36d9d5d612e0909f5698d1d433`
- v1.1: `0c2281e47ff4e2b4b8153fbde6350d5c9c1a4341`
- Classification: VERIFIED COMPLETE for baseline capture.

## DEC-R1-002 — Reconstruct Rather Than Rebase
- Decision: Reconstruct the 14 verified maintenance files from current canonical main.
- Basis: Historical maintenance history diverged and omitted later governance records.

## DEC-R1-003 — Correct Canonical Risk-TCO Source Preservation
- Decision: Preserve `Risk-Adjusted TCO (USD)` before rebuilding selected-currency outputs.
- Scope boundary: No FX formula, ranking, threshold, schema, recommendation or award-control change.
- Classification: VERIFIED COMPLETE.

## DEC-R1-004 — Executable Candidate Evidence
- Environment: Python 3.11.15 with pinned requirements.
- Result: compile PASS; 162 passed, 0 failed, 0 skipped, 1 warning; Streamlit smoke PASS.
- Classification: VERIFIED COMPLETE.

## DEC-R1-005 — Standalone Main Baseline Evidence
- Date: 2026-07-15
- Decision: Independently execute the exact unchanged main SHA rather than rely only on historical acceptance.
- Result: compile PASS; 114 passed, 0 failed, 0 skipped, 1 warning; Streamlit smoke PASS.
- Evidence: workflow run `29403967641`, artifact digest `sha256:7f0463c8f7baa3c863925de3d7c42afc921fc954f90cafb9b71c50c47878f8d4`.
- Classification: VERIFIED COMPLETE.

## DEC-R1-006 — Hosted Candidate Acceptance
- URL: `https://ai-procurement-copilot-pr9.streamlit.app/`
- Deployment evidence: correct Recovery R1 branch, Python 3.11.15, dependency installation and server startup confirmed.
- Owner acceptance: all six supplier profiles and USD/INR/Both modes manually checked and reported correct.
- Evidence boundary: functional hosted acceptance was observed by the project owner, not independently reproduced through the connected GitHub tool.
- Classification: VERIFIED COMPLETE.

## DEC-R1-007 — Promotion Recommendation
- Decision: **MERGE READY** for v1.0.1 promotion.
- Basis: exact baselines, standalone main evidence, candidate regression/smoke evidence, clean scope boundary, hosted deployment evidence and owner-observed hosted acceptance.
- Final PR workflow diff must remain absent.
- PR #9 remains draft and unmerged until explicit owner merge authorization.
- Version 1.1 implementation remains OUT OF SCOPE.
