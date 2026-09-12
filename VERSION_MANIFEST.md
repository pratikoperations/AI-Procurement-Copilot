# Version Manifest

## Project
AI Procurement Copilot

## Current Product Position
**Stabilized portfolio/interview product under controlled freeze.**

The repository has progressed beyond the earlier v1.0.1 release-closure state. Historical v1.0.0, v1.0.1, v1.1 and v1.2 records remain evidence of prior governed stages and must not be rewritten as if they were current release candidates.

## Current Canonical References
- Repository: `pratikoperations/AI-Procurement-Copilot`
- Stable branch: `main`
- Current `main` HEAD at Codex-governance bootstrap: `e75d930d06403bbefe919bace4d134d118e987df`
- Current public portfolio baseline documented by the application: `dc05fcb86e5be53212443834b3d6c46cc5aeca5c`
- Latest accepted exact-head validation source: `b895815fe1c0511b7f025c53773ca2e5ba60dbdc`
- Frozen v1.2 historical baseline: `4803b1d72fa8a6509d9d7faf0e9decc677c447be`
- Frozen v1.1 historical baseline: `b85cd37aaae709058eb15350d680b18c03da46ba`

## Current Capability Position
The stabilized portfolio build includes governed RFQ comparison, category-aware procurement analysis, should-cost/TCO/risk/scoring workflows, scenario and allocation support, negotiation intelligence, governed ERP workbook review boundaries, calculation provenance/traces/reconciliation, a Governed Calculation Explorer and project-wide read-only SourceMate.

## Current Governance Boundary
- Human procurement approval is mandatory.
- No autonomous sourcing, supplier qualification, award or approval.
- No live SAP/Oracle write-back.
- No production allocation execution.
- Formula metadata is documentation only and is not executable authority.
- SourceMate is read-only and does not use external LLMs, web browsing, RAG or hidden recalculation.
- Unsupported/deferred coverage must remain explicitly labelled rather than fabricated.
- Public demonstration must use synthetic or sanitized data.

## Current Accepted Validation Evidence
For the code tree that produced the current public baseline:
- Quality Checks run 1117 / run ID `32959567882`
- Python 3.11.16
- 1534 tests passed, 0 failures
- compilation passed
- Ruff governed checks passed
- targeted mypy checks passed
- dependency audit reported no known vulnerabilities
- Streamlit smoke passed
- Mobile Browser Acceptance run 136 / run ID `32959567861`, passed
- two non-failing warnings retained

Validation is exact-head evidence. Later commits require their own evidence before being described as equivalently validated.

## Historical Release Integrity
- v1.0.0 remains the first stable Portfolio Edition baseline.
- v1.0.1 remains a governed maintenance milestone.
- v1.1 remains the completed ERP structural foundation / read-only ERP Upload Preview historical stage.
- v1.2 remains the completed Portfolio Presentation Release historical stage.
- Later stabilized work is additive and does not convert the portfolio application into production enterprise software.
- No historical tag, release record or baseline may be moved or rewritten without explicit owner authorization.

## Current Change Policy
The project is under stabilization freeze. Permitted work must be separately authorized and bounded to defect correction, security/privacy hardening, evidence/test/governance improvement, documentation reconciliation or other clearly justified launch/interview-readiness work. Routine feature expansion is closed.

## Codex Bootstrap
- Branch: `codex/governance-bootstrap`
- Draft PR: #108
- Purpose: establish Codex operating rules and reconcile current control documents.
- Expected product impact: none.

## Next Controlled Action
Complete exact-head verification of PR #108 and merge only after confirming its diff is limited to approved governance/documentation changes and no runtime or business-rule behaviour changed.
