# Project Control

## Purpose

This document is the current operational index for `pratikoperations/AI-Procurement-Copilot`. It records verified repository state, programme closure, accepted contracts, CI evidence, limitations and deferred work. It does not replace immutable Git objects, executed CI, executable contracts, code, tests, architecture records, business rules or human procurement approval.

## Source-of-Truth Hierarchy

1. Immutable Git objects and current refs.
2. Executed CI and validation evidence tied to exact SHAs.
3. Executable contracts, code and tests.
4. `PROJECT_CONTROL.md`.
5. ADRs, architecture, business rules and recovery records.
6. PR descriptions and closure records.
7. Conversation history.

When sources conflict, the higher source prevails. A narrative statement cannot override an exact ref, executable behaviour or CI result.

## Staleness and Self-Reference Rule

Any change to `main`, an active branch, active PR, accepted head, merge-test SHA, changed-file boundary or accepted CI evidence invalidates the affected current-state statement until reverified.

A document cannot reliably embed the SHA of the commit currently modifying itself. Therefore:

- this file records the accepted programme implementation baseline and the exact evidence used to close it;
- the governance closure branch head, closure PR merge-test SHA and resulting post-closure `main` SHA remain externally governed by Git, CI and the closure PR record until post-merge verification is complete;
- after the closure PR merges, Git and the closure PR record govern the resulting `main` SHA even if the implementation-baseline SHA below remains unchanged.

## Identity and Classification

- Repository: `pratikoperations/AI-Procurement-Copilot`.
- Default branch: `main`.
- Project purpose: governed, explainable procurement decision support for sourcing analysis, supplier comparison, category calculations, risk, scenarios, multi-supplier allocation, traceability and business-readable outputs.
- Engineering classification: modular deterministic decision-support application with governed AI-assisted development.
- Portfolio classification: governed interview showcase / portfolio decision-support prototype.
- Enterprise-production classification: not production-ready and not represented as an enterprise production system.
- Human procurement approval: mandatory.
- Autonomous supplier award: prohibited.
- ERP writeback: not implemented or authorized.
- Realized-savings claims: prohibited without organizational evidence.

## Authoritative Repository State Before Programme-Closure PR

- Verified default branch: `main`.
- Verified `main` SHA: `71e02a4607b517e611297148cb0cd2ceb8a179d7`.
- Latest implementation merge: PR `#56` — Gate 3C2B canonical export and decision-package reconciliation.
- PR `#56` state: closed and merged.
- PR `#56` feature head: `84ce2f10e4b9ab8513aeab51190a3f3cb9a94fdd`.
- PR `#56` governing merge-test SHA: `69d6c56d5d5150870a4ef4aa4dfee3945c53b7ad`.
- PR `#56` resulting merge commit: `71e02a4607b517e611297148cb0cd2ceb8a179d7`.
- No later commit was present on `main` when the closure branch was created.
- Open PR `#1` remains historical, draft and unmerged; it is not an active blocker for this programme closure and must not be represented as current architecture authority.

## Shared Cross-Category Multi-Supplier Award and Allocation Programme

### Final Status

**COMPLETE WITH DOCUMENTED DEFERRALS**

The repository programme is complete for the governed portfolio/interview scope. All authorized allocation gates are implemented, accepted, merged and reconciled. No active technical blocker remains within the programme boundary.

The programme is not an enterprise-production implementation. Production identity, RBAC, persistent approval workflow, live ERP integration, operational monitoring, HA/DR, audited supplier evidence and production deployment remain outside this programme.

### Completed Gates

- Gate 1 — shared immutable allocation request, supplier-input and feasibility contracts.
- Gate 2 — deterministic exactly-K allocation engine.
- Gate 3A — common governed route adapter and contract.
- Gate 3B1 — canonical application allocation route integration.
- Gate 3B2 — governed allocation presentation and operational reconciliation.
- Gate 3C1 — canonical scenario allocation route.
- Gate 3C2A — canonical scenario presentation reconciliation.
- Gate 3C2B — canonical export and decision-package reconciliation.

### Accepted Contract Versions

- Allocation request and feasibility contract: `AIPC-MULTI-ALLOC-1.0`.
- Allocation engine contract: `AIPC-MULTI-ALLOC-ENGINE-1.0`.
- Common route adapter: `AIPC-MULTI-ALLOC-ADAPTER-1.0`.
- Scenario allocation contract: `AIPC-MULTI-ALLOC-SCENARIO-1.0`.
- Scenario presenter contract: `AIPC-MULTI-ALLOC-SCENARIO-PRESENTER-1.0`.
- Export contract: `AIPC-MULTI-ALLOC-EXPORT-1.0`.

### Final Authority Chain

Scenario or live category input
→ governed category scoring and eligibility evidence
→ common route adapter
→ feasibility controls
→ deterministic exactly-K allocation
→ canonical application or scenario result
→ canonical presentation projection
→ canonical JSON and Excel export.

No UI, intelligence or export layer is authorized to reconstruct allocation, infer evidence origin, create fallback allocation or act as a second allocation authority.

## Gate 3C2A Closure Evidence

- PR: `#55`.
- Resulting `main` SHA: `1dbb454b0cbde0a9d2b8c2708f62199d48580872`.
- Accepted head: `bb0768c88a2af7da01504759df53551004c80a94`.
- Accepted merge-test SHA: `d8f2491aefeabf353f6367b77b4132133b09907e`.
- Quality Checks run: `884`.
- Run ID: `30759674118`.
- Job ID: `91527833682`.
- Python: `3.11.15`.
- Result: `1387 passed`, `0 failures`, `0 errors`.
- Compilation: passed.
- Streamlit smoke: passed.
- Warning boundary: one pre-existing pandas `FutureWarning`; no new Gate 3C2A warning.

## Gate 3C2B Closure Evidence

### Accepted Implementation Package

Exactly eight files entered the merge:

- `app.py`;
- `modules/export_evidence_registry.py`;
- `modules/exports.py`;
- `tests/test_app_multi_supplier_allocation_route.py`;
- `tests/test_c2_final_ux_exports.py`;
- `tests/test_c2_strict_json_exports.py`;
- `tests/test_eas_biv_gate1a_registries.py`;
- `tests/test_eas_biv_gate3_evidence.py`.

No unrelated application, category, scenario, Steel, RFQ, dependency, workflow, deployment or governance file entered PR `#56`.

### Accepted Validation

- Workflow: Quality Checks.
- Run number: `893`.
- Run ID: `30822026026`.
- Job ID: `91714045800`.
- Accepted feature head: `84ce2f10e4b9ab8513aeab51190a3f3cb9a94fdd`.
- Accepted merge-test SHA: `69d6c56d5d5150870a4ef4aa4dfee3945c53b7ad`.
- Python: `3.11.15`.
- Result: `1388 passed`, `0 failures`, `0 errors`.
- Compilation: passed.
- Streamlit smoke: passed.
- Warning boundary: one pre-existing pandas `FutureWarning`; no new Gate 3C2B warning.

Runs `889`, `891` and `892` are historical or diagnostic evidence and are subordinate to successful current-head run `893`.

### Post-Merge Verification

- PR `#56` was re-fetched and confirmed closed and merged.
- Merge commit and parent package were inspected.
- The merge boundary was confirmed as exactly the accepted eight files.
- The feature branch was retained.
- No pull-request-triggered workflow dispatch was returned for merge commit `71e02a4607b517e611297148cb0cd2ceb8a179d7`.
- The governance-only closure PR is the authorized equivalent validation path for the accepted merged code plus this one-file control update.
- The closure PR must run the existing full Quality Checks before merge.

## Functional Assurance State

The accepted repository state confirms:

- canonical multi-supplier allocation is the sole C2 allocation authority;
- scenario presentation uses the canonical Gate 3C1 result and Gate 3C2A presenter;
- C2 JSON exposes `canonical_allocation` and governed `scenario_allocations`;
- C2 Excel exposes `Canonical Allocation` and `Scenario Allocations`;
- C2 export no longer serializes `visible_winner`, `standard_allocation` or `optimized_allocation` as allocation authorities;
- analytical ranking remains distinct from supplier allocation and award approval;
- blocked and non-applicable states do not expose allocation rows;
- strict JSON rejects non-finite JSON values and normalizes unavailable values;
- Steel export contracts remain unchanged;
- non-C2 export behaviour remains backward compatible;
- human procurement review remains mandatory;
- no autonomous award, ERP writeback or realized-savings claim is created.

## Definition of Done and Verification Reconciliation

The programme satisfies `DEFINITION_OF_DONE.md` for code-gate and programme-closure evidence because:

- every authorized allocation gate is accepted and merged;
- exact contracts, PRs, heads, merge-test SHAs, resulting implementation baseline and CI evidence are recorded;
- exact merge boundaries were verified;
- residual risks and deferred work are preserved;
- no active programme PR is falsely represented as merged;
- the closure update is documentation-only and must pass existing CI;
- post-closure resulting `main` must be recorded externally in the closure PR and final verification report.

The programme satisfies `VERIFICATION_POLICY.md` because:

- the changed `main` SHA was re-fetched;
- the merge commit and exact file boundary were inspected;
- PR state, branch, head, merge-test and CI were revalidated;
- the absence of automatic post-merge workflow dispatch was explicitly recorded;
- the closure PR provides fresh validation against the merged implementation plus the updated control record.

## Governance Records Inspected

- `PROJECT_CONTROL.md` — stale before this reconciliation; updated by the closure package.
- `DEFINITION_OF_DONE.md` — current and sufficient; no change required.
- `VERIFICATION_POLICY.md` — current and sufficient; no change required.
- `SIMPLICITY_GATE.md` — no new implementation complexity is introduced by closure; no change required.
- `TEST_RISK_REGISTER.md` — no such repository file was found at closure review; no file was invented solely for closure.
- Relevant ADR references — no new architecture decision is introduced by closure, so no ADR change is required. Existing executable contracts and merged PR records remain authoritative for the implemented allocation architecture.

## Residual Risks and Limitations

- Portfolio/interview use is supported; enterprise production readiness is not claimed.
- Supplier, capacity, ESG, performance and risk evidence may be synthetic, supplied or incomplete unless independently verified.
- Human procurement approval remains outside automated execution.
- No enterprise identity, RBAC, production database, persistent workflow, live ERP writeback, production observability, HA or DR is implemented.
- No physical Android, browser or accessibility certification is implied by automated tests and Streamlit smoke.
- The historical `Winning Supplier` compatibility label may remain in non-export analytical consumers and must be interpreted as an analytical ranking signal, not an approved award.
- Open PR `#1` is historical governance debt and remains draft/unmerged; it is not part of this programme closure.
- Post-merge workflow dispatch is limited by the repository workflow trigger; absence of a merge-commit run is documented rather than hidden.

## Explicit Deferrals

The following are deferred and are not blockers to closing this allocation programme:

- Gate 0E — later governance enhancement work.
- Gate 0F — historical-document and handoff-guide reconciliation.
- Power BI portfolio dashboard work.
- Facility Management Services or any additional procurement category.
- Live ERP integration.
- Authentication, RBAC and production approval persistence.
- Production deployment, observability, HA and DR.
- External supplier evidence verification and realized-savings assurance.

No deferred item is authorized by this closure record.

## Programme Completion Classification

- Portfolio/interview allocation capability: `100% complete` for the authorized programme scope.
- Current repository allocation programme: `100% complete` after governance closure merge and post-merge verification.
- Enterprise-production readiness: `not complete`; separate productization programme required.
- Remaining active engineering hours within this allocation programme after closure merge: `0`.
- Deferred future work is excluded from the programme completion percentage and must be separately authorized.

## Closure Branch Scope

The governance closure package is restricted to:

- `PROJECT_CONTROL.md` only;
- one governance-only branch;
- one draft closure PR;
- existing full Quality Checks;
- governed review and separately authorized irreversible merge;
- post-merge verification and final programme freeze.

No application logic, category engine, allocation engine, scenario engine, export code, RFQ contract, dependency, workflow or deployment change is authorized.

## Final Programme Status

**COMPLETE WITH DOCUMENTED DEFERRALS**

The Shared Cross-Category Multi-Supplier Award and Allocation programme is frozen at the accepted implementation baseline `71e02a4607b517e611297148cb0cd2ceb8a179d7`, subject only to completion and merge of this governance-only closure record. Any later change to the allocation contracts, authority chain, presentation or export schema requires a new governed programme or explicitly authorized reopening decision.
