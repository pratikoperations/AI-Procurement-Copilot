# Decision Log

This file records major project decisions and their rationale.

## DEC-001 — Use GitHub as Canonical Source of Truth

**Decision:** GitHub will be the master storage location for all project files, source code, documentation, build plans, logs, and recovery instructions.

**Why:** Prevents loss of work if chat context is lost. Enables version history, recovery, and professional project governance.

## DEC-002 — Build as Portfolio Edition v1.0

**Decision:** The first public release will be named Portfolio Edition v1.0.

**Why:** This is clearer and more credible than continuing internal version labels such as V9.5.

## DEC-003 — Category-Engine Expansion

**Decision:** Packaging Procurement and Raw Material Procurement operate through the same category-engine architecture. New categories must reuse shared procurement logic while preserving category-specific cost, risk, and technical rules.

**Why:** Prevents duplicated products and allows controlled platform expansion.

## DEC-004 — Transparent Rule-Guided AI-Ready Architecture

**Decision:** Award and calculation logic will remain deterministic, visible, and auditable. AI will support extraction, drafting, explanation, retrieval, and summarization, not autonomous award or technical approval decisions.

**Why:** Procurement and packaging decisions require governance, explainability, accountability, and human control.

## DEC-005 — Modular Architecture

**Decision:** Build as a modular software product, not a single-use Streamlit script.

**Why:** Modular design improves maintainability, extensibility, interview credibility, and future conversion to other interfaces.

## DEC-006 — Packaging Value Engineering Is a Copilot Module

**Decision:** Packaging Value Engineering & Decision Intelligence will be built inside `pratikoperations/AI-Procurement-Copilot`. It will not use a separate product or repository.

**Why:** The Procurement Copilot owns horizontal sourcing, supplier, TCO, negotiation, allocation, and savings workflows. Packaging Value Engineering provides the specialist technical-commercial decision layer. A unified platform reduces duplication and creates a stronger end-to-end story.

## DEC-007 — Scope-Gated Development

**Decision:** The project will support five controlled scopes: Lean Interview Module, Robust Interview Version, Complete Integrated Portfolio Version, Production Pilot, and Enterprise Scale-Up.

**Why:** Scope gates prevent interview work from becoming premature enterprise engineering and allow investment to follow validated value.

## DEC-008 — Build 0.9.5 Must Be Closed Before Expansion

**Decision:** No Packaging Value Engineering implementation begins until Build 0.9.5 CI and live Supplier Intelligence validation are completed and Portfolio Edition v1.0 is hardened.

**Why:** Completing and validating the existing platform produces higher value than starting overlapping functionality on an unstable base.

## DEC-009 — Commit and Quality Check Every Meaningful Update

**Decision:** Every meaningful update must be tested, documented, committed, pushed, re-verified from GitHub, and accompanied by QA evidence. Chat-only or uncommitted work is not complete.

**Why:** This keeps GitHub authoritative and makes the project recoverable even if chat context is lost.

## DEC-010 — Technical Qualification Precedes Commercial Ranking

**Decision:** Packaging and supplier alternatives must pass technical qualification or be explicitly conditionally qualified before commercial ranking and allocation.

**Why:** Prevents low-price recommendations that are technically unsafe or insufficiently validated.

## DEC-011 — Savings Require Realization Evidence

**Decision:** Identified or approved savings are not treated as delivered until implementation date, actual price, actual volume, one-time costs, and relevant validation evidence are recorded.

**Why:** This connects recommendations to measurable business outcomes and reduces savings leakage.
