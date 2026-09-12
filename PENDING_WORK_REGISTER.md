# Pending Work Register

This register reflects the **current stabilized portfolio state**. Historical v1.0.1 closure tasks remain preserved in Git history and are not active blockers.

Formal status values use the approved classification taxonomy.

| ID | Work item | Current status | Evidence / dependency | Acceptance criterion |
|---|---|---|---|---|
| GOV-001 | Establish root-level Codex operating rules | IMPLEMENTED BUT UNTESTED | PR #108 / `AGENTS.md` | Rules reviewed and merged without runtime impact |
| GOV-002 | Reconcile active status/version/recovery documents | IMPLEMENTED BUT UNTESTED | PR #108 | Active control documents agree with current stabilized state |
| GOV-003 | Verify PR #108 exact head and diff boundary | NOT STARTED | Final PR head | Only approved governance/documentation files changed; no runtime/business logic impact |
| GOV-004 | Merge Codex governance bootstrap | NOT STARTED | GOV-003 + owner approval | Exact verified head merged to `main` |
| GOV-005 | Use governed Codex workflow for next authorized task | NOT STARTED | GOV-004 | Focused branch, acceptance criteria, tests, diff review and exact-head merge discipline used |
| STAB-001 | Preserve stabilization freeze | VERIFIED COMPLETE | Current README/governance state | No routine feature or cosmetic expansion without explicit authorization |
| STAB-002 | Preserve human procurement decision boundary | VERIFIED COMPLETE | Current application/governance | No autonomous award, approval, qualification, production allocation or ERP write-back |
| STAB-003 | Preserve SourceMate read-only boundary | VERIFIED COMPLETE | Current public baseline | No external LLM, RAG, web browsing, hidden recalculation or transaction authority |
| QA-001 | Preserve accepted public-baseline validation evidence | VERIFIED COMPLETE | Source head `b895815f...`; Quality Checks run 1117 | Evidence remains tied to exact validated head and is not overstated for later commits |
| QA-002 | Run task-specific verification for future Codex changes | DEFERRED | Next authorized implementation task | Tests/checks match change risk and repository requirements |
| SEC-001 | Maintain synthetic/sanitized public-demo data boundary | VERIFIED COMPLETE | Current public warnings/governance | No confidential supplier, contract, personal, credential or commercially sensitive data introduced |
| REL-001 | Historical v1.0.0 / v1.0.1 / v1.1 / v1.2 records | VERIFIED COMPLETE | Git history and frozen baselines | Historical records remain unchanged unless explicitly governed |
| FUT-001 | New feature expansion | DEFERRED | Separate business case + owner authorization | Must pass objective, scope, architecture and governance review before implementation |
| OOS-001 | Autonomous procurement execution / live ERP write-back | OUT OF SCOPE | Governance boundary | Must not be introduced by Codex or any other agent |

## Priority Rule
Complete `GOV-003` and `GOV-004` before using Codex for new implementation. After bootstrap, each new task must be independently authorized; this register does not grant blanket permission for feature development.
