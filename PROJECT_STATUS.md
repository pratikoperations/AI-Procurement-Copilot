# Project Status

## Canonical Repository State
- Repository: `pratikoperations/AI-Procurement-Copilot`
- Canonical stable branch: `main`
- Current `main` HEAD at Codex-governance bootstrap: `e75d930d06403bbefe919bace4d134d118e987df`
- Current public portfolio baseline documented by the application: `dc05fcb86e5be53212443834b3d6c46cc5aeca5c`
- Latest accepted exact-head validation source: `b895815fe1c0511b7f025c53773ca2e5ba60dbdc`
- Frozen v1.2 historical baseline: `4803b1d72fa8a6509d9d7faf0e9decc677c447be`
- Frozen v1.1 historical baseline: `b85cd37aaae709058eb15350d680b18c03da46ba`
- Hosted application: `https://ai-procurement-copilot.streamlit.app/`

## Current Operating Mode
**STABILIZATION FREEZE / PORTFOLIO-INTERVIEW PRODUCT**

Routine feature expansion and cosmetic churn are closed. Only separately authorized, bounded work is permitted, such as:
- verified defect correction;
- security or privacy hardening;
- material documentation reconciliation;
- launch/interview readiness correction;
- test or governance improvements that do not silently change product behaviour.

Any scope expansion requires explicit approval before implementation.

## Current Product Boundary
- Governed procurement decision support only.
- Human procurement approval remains mandatory.
- No autonomous supplier qualification, award or approval.
- No production allocation execution.
- No live ERP write-back.
- SourceMate remains read-only and deterministic; it does not browse the web, call an external LLM, use RAG, recalculate authoritative procurement results or execute procurement actions.
- Synthetic or sanitized data only for public demonstration; confidential supplier, contract, personal, credential or commercially sensitive data must not be uploaded.

## Current Accepted Quality Evidence
Latest accepted exact-head evidence for the code tree that produced the current public baseline:
- Validated source head: `b895815fe1c0511b7f025c53773ca2e5ba60dbdc`
- Resulting public baseline: `dc05fcb86e5be53212443834b3d6c46cc5aeca5c`
- Quality Checks run 1117 / run ID `32959567882`
- Python 3.11.16
- 1534 tests passed, 0 failures
- Python compilation passed
- Ruff governed checks passed
- Targeted mypy checks passed
- Dependency audit reported no known vulnerabilities
- Canonical Streamlit smoke test passed
- Mobile Browser Acceptance run 136 / run ID `32959567861`, passed
- Two non-failing warnings were retained, including the pre-existing pandas FutureWarning

This evidence is historical exact-head evidence. It must not be represented as validation of later commits unless those commits are separately tested.

## Governance State
- GitHub is the canonical source of truth.
- `main` is the stable branch.
- Focused branch + pull request workflow is required for meaningful changes.
- Exact-head verification is required before merge when the head can move.
- No direct push to `main` for governed Codex work.
- No force push, history rewrite, tag creation, release creation or deployment without explicit authorization.
- Procurement formulas, schemas, thresholds, rankings, recommendation eligibility and approval controls must not be invented or changed implicitly.

## Codex Governance Bootstrap
- Governance branch: `codex/governance-bootstrap`
- Draft PR: #108
- Purpose: add project-specific Codex operating rules and reconcile active recovery/control documents before Codex resumes implementation work.
- Functional impact: none intended; documentation/governance only.

## Documentation Authority
For current operating state, use the following order:
1. current executable behaviour and tests at the exact commit being assessed;
2. latest accepted Git/CI evidence tied to an exact SHA;
3. `README.md`;
4. `PROJECT_STATUS.md`;
5. `VERSION_MANIFEST.md`;
6. current architecture, governance and test-evidence documents.

Historical recovery, release and planning records remain evidence of prior stages and must not override later accepted state.

## Next Controlled Action
Complete and verify PR #108 as a documentation/governance-only Codex bootstrap. Do not resume feature development until the active control documents and `AGENTS.md` are consistent and the PR is approved under exact-head governance.
