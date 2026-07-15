# Decision Log

This file records major project decisions and their rationale. Earlier verified decisions are preserved; recovery decisions are appended.

## DEC-001 — Use GitHub as Canonical Source of Truth
**Decision:** GitHub is the master location for code, documentation, plans, logs and recovery instructions.

## DEC-002 — Portfolio Edition v1.0
**Decision:** The first stable public release is Portfolio Edition v1.0.0.

## DEC-003 — Category Expansion
**Decision:** Packaging was the initial engine; raw-material capability was subsequently included in the stable release through the modular category architecture.

## DEC-004 — Transparent Rule-Guided Architecture
**Decision:** Award logic remains deterministic, visible and auditable. AI may assist extraction, drafting, explanation and summarization, but may not autonomously approve supplier awards.

## DEC-005 — Modular Architecture
**Decision:** Maintain a modular product rather than a single-use Streamlit script.

## DEC-006 — Defer Time-Aware Procurement Analytics
**Decision:** Date-range and historical period analytics remain deferred until explicitly authorized after the stable release.

Design constraints:
- Every module must declare its governing date field.
- Missing dates must not be silently assigned.
- Incomplete periods must be labelled.
- Non-comparable periods must suppress comparisons.
- Screens and exports must disclose reporting period and coverage.

## DEC-007 — Preserve Portfolio Edition v1.0.0
- Date: 2026-07-15
- Decision: Keep `main` as the canonical stable Portfolio Edition v1.0.0 line.
- Basis: Stable release documents and validation history.
- Consequence: No feature development may be merged directly into `main`; only documented defects, security fixes and deployment fixes are eligible.

## DEC-008 — Recognize Version 1.1 as real but partial
- Date: 2026-07-15
- Decision: Recognize `v1.1-development` as an existing branch with partial ERP intake implementation.
- Classification: VERIFIED PARTIAL for the ERP foundation; VERIFIED COMPLETE for branch existence.
- Basis: GitHub compare resolves the branch as 27 commits ahead of the common release base and shows schema, mapping, loader, validator, samples, specifications and focused tests.
- Consequence: Main documentation describing all v1.1 work as future-only is incomplete. Sprint 1 is not accepted as complete.

## DEC-009 — Reject unsupported completion claims
- Date: 2026-07-15
- Decision: Treat claims of Sprint 1 batches 1–6 completion, complete upload pipeline, validation reporting, upload UI and `147 passed, 0 failed, 1 warning` as non-authoritative until repository evidence exists.
- Classification: REPORTED BUT NOT FOUND.

## DEC-010 — Treat currency corrections as v1.0.1 maintenance
- Date: 2026-07-15
- Decision: Keep currency-display corrections on `maintenance/v1.0.1`.
- Main classification: DEFECT / REGRESSION.
- Maintenance implementation classification: IMPLEMENTED BUT UNTESTED.
- Basis: Merged PRs #5–#7 target that branch and preserve calculations, rankings, audit metadata and selector behavior.
- Consequence: Full tests and live validation are mandatory before promotion.

## DEC-011 — Separate supplier-selector claim from capability
- Date: 2026-07-15
- Missing-selector claim classification: REPORTED BUT NOT FOUND.
- Supplier-selector capability classification: VERIFIED COMPLETE.
- Basis: Main contains `st.selectbox("Select Supplier 360 Profile", supplier_names, index=0)` and selects the matching profile.
- Consequence: Runtime validation remains a pending action; do not build a duplicate selector without reproducing a specific defect.

## DEC-012 — Branch Strategy
1. Preserve `main`.
2. Capture exact current HEADs for `maintenance/v1.0.1` and `v1.1-development` without substituting merge or merge-base SHAs.
3. Obtain approval to validate and reconcile `maintenance/v1.0.1`.
4. Establish an approved v1.0.1 maintenance baseline.
5. Rebase or reconstruct `v1.1-development` from that baseline before further feature work.

## DEC-013 — Documentation Recovery Branch
- Date: 2026-07-15
- Decision: Recovery-control changes only occur on `docs/project-recovery-2026-07-15`, created from main SHA `39bfc2d0c75e58c883fdcec797f66dff2edd9eec`.
- Consequence: Recovery PR remains documentation-only and draft until reviewed.

## DEC-014 — Proposed Next Controlled Build — Pending Owner Approval
- Date: 2026-07-15
- Proposal: Recovery Build R1 covering exact SHA capture, test/deployment verification, maintenance reconciliation and v1.0.1 closure planning.
- Approval state: Pending explicit project-owner approval.
- Excluded scope classification: OUT OF SCOPE for this proposed build unless separately authorized.
- Excluded scope: ERP feature implementation, new analytics, new AI providers and architectural expansion.

## DEC-015 — Deployment Evidence Classification
- Historical Streamlit architecture and smoke acceptance: DOCUMENTED ONLY.
- Current hosted deployment-health claim: REPORTED BUT NOT FOUND.
- Consequence: Current runtime verification remains a pending validation action.

## DEC-016 — Mandatory Project-Memory Updates
Every substantive build must update:
- `PROJECT_STATUS.md`
- `PROJECT_ACTIVITY_LOG.md`
- `PENDING_WORK_REGISTER.md`
- `PROJECT_RECOVERY_MANIFEST.md`

A build lacking these updates is not governance-complete.