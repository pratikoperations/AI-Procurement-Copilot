# Project Recovery Manifest

## Purpose
This manifest defines how to recover the **current stabilized portfolio project after MRO-0**, not how to resume an obsolete release-closure or bootstrap task.

## Repository Identity
- Repository: `pratikoperations/AI-Procurement-Copilot`
- Canonical source of truth: GitHub
- Canonical stable branch: `main`
- Current accepted `main` HEAD: `d6d1e741205e6c0ceb37a8d3617e9aafd6d26e55`
- Latest governed extension: MRO-0 / PR #109
- MRO-0 source head: `9a35873b8ae08a3fd7c5bc9747287ad4fe9880c0`
- Post-merge Quality Checks run 1138 / run ID `38204618690` — SUCCESS
- Frozen v1.2 historical baseline: `4803b1d72fa8a6509d9d7faf0e9decc677c447be`
- Frozen v1.1 historical baseline: `b85cd37aaae709058eb15350d680b18c03da46ba`

## Approved Classification Taxonomy
When a formal status classification is required, use exactly one of:
- VERIFIED COMPLETE
- VERIFIED PARTIAL
- IMPLEMENTED BUT UNTESTED
- DOCUMENTED ONLY
- REPORTED BUT NOT FOUND
- NOT STARTED
- DEFECT / REGRESSION
- DEFERRED
- OUT OF SCOPE

## Recovery Read Order
Start recovery in this order:
1. `AGENTS.md`
2. `README.md`
3. `PROJECT_STATUS.md`
4. `VERSION_MANIFEST.md`
5. `CONTRIBUTING.md`
6. current architecture and governance documentation
7. latest test-evidence documents and GitHub Actions evidence tied to exact SHAs
8. `PENDING_WORK_REGISTER.md`
9. `DECISION_LOG.md`, `BUILD_HISTORY.md` and `CHANGELOG.md` for historical context
10. older recovery/planning records only as historical evidence

## Recovery Authority Rules
- Current executable behaviour and exact-head evidence take precedence over stale planning text.
- GitHub history is authoritative over chat history.
- Do not infer that an old release or governance plan is active merely because it remains in history.
- Do not silently reconcile contradictory documents; update active control documents through a focused PR.
- Never move or rewrite historical release/tag baselines as part of recovery.

## Current Operating Mode
**Stabilization freeze / portfolio-interview product.**

The functional portfolio build is complete at the currently approved scope. Routine feature expansion is closed. Bounded work requires explicit authorization and should be limited to verified defect correction, security/privacy hardening, documentation reconciliation, testing/evidence improvement, governance improvement or material launch/interview-readiness correction.

## Current Product Boundaries
- Human procurement approval remains mandatory.
- No autonomous supplier award, approval or qualification.
- No live ERP write-back.
- No production allocation execution.
- SourceMate remains read-only and deterministic, without external LLM, RAG, web-browsing or hidden recalculation authority.
- MRO / Industrial Supplies remains Foundation Preview only.
- No MRO should-cost, supplier scoring, scenario, negotiation or allocation execution is active.
- Approved Equivalent substitution remains human-approved.
- Synthetic or sanitized data only for public demonstration.

## Current Accepted Validation Anchor
For the current MRO-0 baseline:
- source head `9a35873b8ae08a3fd7c5bc9747287ad4fe9880c0`;
- PR Quality Checks run 1137 / run ID `38203428348` — SUCCESS;
- PR Mobile Browser Acceptance run 153 / run ID `38203428355` — SUCCESS;
- resulting main `d6d1e741205e6c0ceb37a8d3617e9aafd6d26e55`;
- main Quality Checks run 1138 / run ID `38204618690` — SUCCESS.

Hosted behavior remains a separate manual acceptance gate. Do not project CI validation into hosted acceptance.

## Historical Recovery Records
Earlier Recovery R1, v1.0.1 closure, v1.1, v1.2 and PR #108 bootstrap records remain preserved as historical evidence. Their old “next action” instructions are no longer current operating instructions unless explicitly re-authorized.

## Completed Governed Extensions
- PR #108 — Codex governance bootstrap — complete.
- PR #109 — MRO-0 Industrial Supplies Foundation Preview — complete.

## Recovery Decision
Resume any future implementation only from the then-current `main`, on a focused branch, with explicit acceptance criteria and exact-head verification.

No feature build, including MRO-1, is pre-authorized. The next evidence-oriented action is manual hosted acceptance of the post-MRO-0 deployed application when practical.
