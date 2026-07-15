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

## DEC-R1-006 — Hosted Acceptance Boundary
- Authoritative hosted Streamlit URL: REPORTED BUT NOT FOUND.
- Hosted runtime health: REPORTED BUT NOT FOUND.
- Supplier-by-supplier hosted acceptance: NOT STARTED.
- Hosted USD/INR/Both visual acceptance: NOT STARTED.
- Decision: Do not infer hosted health from CI smoke evidence.

## DEC-R1-007 — Promotion Recommendation
- Decision: **CHANGES REQUIRED** before v1.0.1 promotion.
- Remaining closure:
  1. obtain and directly validate the authoritative hosted URL;
  2. exercise all packaging and raw-material supplier options;
  3. validate USD, INR and Both modes in the hosted interface.
- Final PR workflow diff must remain absent.
- Version 1.1 implementation remains OUT OF SCOPE.
