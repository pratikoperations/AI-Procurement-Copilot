# Project Recovery Manifest

## Purpose
This manifest defines how to recover the **current stabilized portfolio project**, not how to resume an obsolete v1.0.1 closure task.

## Repository Identity
- Repository: `pratikoperations/AI-Procurement-Copilot`
- Canonical source of truth: GitHub
- Canonical stable branch: `main`
- Current `main` HEAD at Codex-governance bootstrap: `e75d930d06403bbefe919bace4d134d118e987df`
- Current public portfolio baseline documented by the application: `dc05fcb86e5be53212443834b3d6c46cc5aeca5c`
- Latest accepted exact-head validation source: `b895815fe1c0511b7f025c53773ca2e5ba60dbdc`
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
6. `ARCHITECTURE.md` and/or current architecture documentation
7. current governance and limitation documentation
8. latest test-evidence documents and GitHub Actions evidence tied to exact SHAs
9. `DECISION_LOG.md`, `BUILD_HISTORY.md` and `CHANGELOG.md` for historical context
10. older recovery/planning records only as historical evidence

## Recovery Authority Rules
- Current executable behaviour and exact-head evidence take precedence over stale planning text.
- GitHub history is authoritative over chat history.
- Do not infer that an old release plan is still active merely because it remains in history.
- Do not silently reconcile contradictory documents; surface the contradiction and update active control documents through a focused PR.
- Never move or rewrite historical release/tag baselines as part of recovery.

## Current Operating Mode
**Stabilization freeze / portfolio-interview product.**

Routine feature expansion is closed. Bounded work requires explicit authorization and should be limited to verified defect correction, security/privacy hardening, documentation reconciliation, testing/evidence improvement, governance improvement or material launch/interview-readiness correction.

## Current Product Boundaries
- Human procurement approval remains mandatory.
- No autonomous supplier award, approval or qualification.
- No live ERP write-back.
- No production allocation execution.
- SourceMate remains read-only and deterministic, without external LLM, RAG, web-browsing or hidden recalculation authority.
- Synthetic or sanitized data only for public demonstration.

## Current Accepted Validation Anchor
Latest accepted exact-head evidence for the code tree that produced the public baseline:
- source head `b895815fe1c0511b7f025c53773ca2e5ba60dbdc`;
- public baseline `dc05fcb86e5be53212443834b3d6c46cc5aeca5c`;
- Quality Checks run 1117 / run ID `32959567882`;
- 1534 tests passed, 0 failures;
- compile, Ruff, targeted mypy, dependency audit and Streamlit smoke passed;
- Mobile Browser Acceptance run 136 / run ID `32959567861`, passed.

Do not project this validation onto later commits without new evidence.

## Historical Recovery Records
Earlier Recovery R1, v1.0.1 closure, v1.1 and v1.2 records remain preserved as historical evidence. Their old “next action” instructions are no longer current operating instructions unless explicitly re-authorized.

## Codex Governance Bootstrap
- Branch: `codex/governance-bootstrap`
- Draft PR: #108
- Scope: `AGENTS.md` plus reconciliation of active control/recovery documentation.
- Runtime/business-rule impact: none intended.

## Recovery Decision
Before resuming active development with Codex, complete PR #108 verification and ensure the active control documents are internally consistent. Any subsequent implementation must start from the then-current `main`, on a focused branch, with explicit acceptance criteria and exact-head verification.
