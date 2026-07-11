# Decision Log

This file records major project decisions and their rationale.

## DEC-001 — Use GitHub as Canonical Source of Truth

**Decision:** GitHub is the master storage location for all project files, source code, documentation, build plans, logs, and recovery instructions.

**Why:** Prevents loss of work if chat context is lost and enables professional version governance.

## DEC-002 — Build Procurement Copilot as Portfolio Edition v1.0

**Decision:** The first public release of AI Procurement Copilot is Portfolio Edition v1.0.

## DEC-003 — Transparent Rule-Guided AI Architecture

**Decision:** Calculations, qualification, scoring, and award logic remain deterministic, visible, and auditable. AI supports extraction, retrieval, drafting, explanation, and summarization—not autonomous award or technical approval.

## DEC-004 — Modular Software Products

**Decision:** Both projects use modular architecture rather than single-use scripts.

## DEC-005 — Separate Project Repositories

**Decision:** AI Procurement Copilot and Packaging Value Engineering & Decision Intelligence will use separate GitHub repositories and separate file systems.

- Existing: `pratikoperations/AI-Procurement-Copilot`
- Recommended new repository: `pratikoperations/Packaging-Value-Engineering-Decision-Intelligence`

**Why:** This prevents same-name file confusion, accidental overwrites, mixed versions, incorrect commits, ambiguous recovery state, and cross-project QA contamination.

## DEC-006 — Integrate Through Versioned Contracts

**Decision:** The projects connect through versioned JSON/CSV decision packages or APIs. They do not share writable folders or directly modify each other's source records.

**Why:** Explicit contracts preserve independence while supporting an end-to-end business workflow.

## DEC-007 — Independent Governance

**Decision:** Each repository maintains its own `README`, project status, activity log, build history, changelog, decision log, version manifest, recovery manifest, tests, QA evidence, CI, and releases.

## DEC-008 — Scope-Gated PVE Development

**Decision:** PVE supports five controlled scopes: Lean Interview Project, Robust Interview Project, Complete Portfolio Project, Production Pilot, and Enterprise Scale-Up.

## DEC-009 — Build 0.9.5 Must Be Closed First

**Decision:** PVE implementation begins only after AI Procurement Copilot Build 0.9.5 CI and live validation are completed and Portfolio Edition v1.0 is hardened.

## DEC-010 — Commit and Quality Check Every Meaningful Update

**Decision:** Every meaningful update must be tested, documented, committed to the correct repository, pushed, re-verified from GitHub, and accompanied by project-local QA evidence.

## DEC-011 — Technical Qualification Precedes Commercial Ranking

**Decision:** Packaging options must be technically qualified or explicitly conditionally qualified before Procurement Copilot uses them in supplier ranking and allocation.

## DEC-012 — Savings Require Realization Evidence

**Decision:** Identified or approved savings are not treated as delivered until implementation, actual price, actual volume, one-time costs, and validation evidence are recorded.
