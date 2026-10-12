# Pending Work Register

This register reflects the **current stabilized portfolio state after MRO-0**. Historical release and closure tasks remain preserved in Git history and are not active blockers.

Formal status values use the approved classification taxonomy.

| ID | Work item | Current status | Evidence / dependency | Acceptance criterion |
|---|---|---|---|---|
| GOV-001 | Establish root-level Codex operating rules | VERIFIED COMPLETE | PR #108 / `AGENTS.md` | Rules merged without runtime impact |
| GOV-002 | Reconcile active status/version/recovery documents | VERIFIED COMPLETE | PR #108 | Bootstrap reconciliation merged |
| GOV-003 | Verify PR #108 exact head and diff boundary | VERIFIED COMPLETE | PR #108 merge history | Approved governance/documentation scope verified |
| GOV-004 | Merge Codex governance bootstrap | VERIFIED COMPLETE | PR #108 | Governed bootstrap merged to `main` |
| GOV-005 | Use governed workflow for a subsequent authorized task | VERIFIED COMPLETE | MRO-0 / PR #109 | Focused branch, exact-head validation, CI, owner authorization and squash merge completed |
| MRO-001 | Establish Industrial Supplies / Industrial Bearings foundation | VERIFIED COMPLETE | PR #109; main `d6d1e741...` | Foundation Preview merged with human approval and fail-closed evidence boundaries |
| MRO-002 | Preserve MRO-0 as foundation-only capability | VERIFIED COMPLETE | Current runtime/tests | No MRO should-cost, scoring, scenario, negotiation or allocation execution |
| HOST-001 | Manually verify post-MRO-0 hosted application | DEFERRED | Hosted Streamlit app | Confirm MRO Foundation Preview and regression-free core journeys in deployed app |
| DOC-001 | Reconcile active control documentation after MRO-0 | IMPLEMENTED BUT UNTESTED | Final-closure reconciliation PR | Current docs agree with post-MRO-0 main and hosted gate status |
| STAB-001 | Preserve stabilization freeze | VERIFIED COMPLETE | Current README/governance state | No routine feature or cosmetic expansion without explicit authorization |
| STAB-002 | Preserve human procurement decision boundary | VERIFIED COMPLETE | Current application/governance | No autonomous award, approval, qualification, production allocation or ERP write-back |
| STAB-003 | Preserve SourceMate read-only boundary | VERIFIED COMPLETE | Current baseline | No external LLM, RAG, web browsing, hidden recalculation or transaction authority |
| QA-001 | Preserve exact-head validation evidence | VERIFIED COMPLETE | PR #109 CI + main run 1138 | Evidence remains tied to exact validated SHAs and is not overstated |
| QA-002 | Run task-specific verification for future changes | DEFERRED | Next authorized task | Tests/checks match change risk and repository requirements |
| SEC-001 | Maintain synthetic/sanitized public-demo data boundary | VERIFIED COMPLETE | Current public warnings/governance | No confidential supplier, contract, personal, credential or commercially sensitive data introduced |
| REL-001 | Preserve historical release records | VERIFIED COMPLETE | Git history and frozen baselines | Historical records remain unchanged unless explicitly governed |
| FUT-001 | New feature expansion, including MRO-1 | DEFERRED | Separate business case + owner authorization | Must pass objective, scope, architecture and governance review before implementation |
| OOS-001 | Autonomous procurement execution / live ERP write-back | OUT OF SCOPE | Governance boundary | Must not be introduced |

## Priority Rule
Complete the current documentation-reconciliation PR under exact-head governance. Hosted acceptance remains a separate manual evidence gate and does not authorize runtime changes by itself.

After closure, no feature build is pre-authorized. Any MRO-1 or other new capability requires a separate business case and explicit owner authorization.
