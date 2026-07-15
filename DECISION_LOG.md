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
- Decision: Record direct branch HEADs for maintenance and v1.1.
- Main start: `075fe16d889cdb82b126fe1e07b0c63dca369580`
- Maintenance: `ba49af44d8c1ff36d9d5d612e0909f5698d1d433`
- v1.1: `0c2281e47ff4e2b4b8153fbde6350d5c9c1a4341`
- Classification: VERIFIED COMPLETE for baseline capture.

## DEC-R1-002 — Reconstruct Rather Than Rebase
- Date: 2026-07-15
- Decision: Reconstruct the 14 verified maintenance files from current canonical main.
- Basis: The historical maintenance branch diverged from main and omitted later portability and recovery-governance records.
- Consequence: Preserve current controls while limiting code/test changes to approved maintenance scope.

## DEC-R1-003 — Correct Canonical Risk-TCO Source Preservation
- Date: 2026-07-15
- Decision: Preserve `Risk-Adjusted TCO (USD)` before removing precomputed display columns, then rebuild selected-currency outputs from a temporary display-only source.
- Basis: Initial full regression and isolated focused tests exposed the loss of the canonical source.
- Scope boundary: No FX formula, supplier ranking, threshold, schema, recommendation or award-control change.
- Classification: VERIFIED COMPLETE after focused and full regression evidence.

## DEC-R1-004 — Executable Candidate Evidence
- Date: 2026-07-15
- Environment: Python 3.11.15 with pinned requirements.
- Result: compile PASS; 162 passed, 0 failed, 0 skipped, 1 warning; Streamlit smoke PASS.
- Classification: VERIFIED COMPLETE for automated candidate evidence.

## DEC-R1-005 — Promotion Recommendation
- Date: 2026-07-15
- Decision: **CHANGES REQUIRED** before v1.0.1 promotion.
- Required closure:
  1. verify authoritative hosted URL and current runtime health;
  2. manually exercise every supplier selector option and matching Supplier 360 profile;
  3. confirm final PR has no workflow diff and canonical CI is green.
- Version 1.1 implementation remains OUT OF SCOPE.
