# Decision Log

This file records major project decisions and their rationale.

## DEC-001 — Use GitHub as Canonical Source of Truth

**Decision:** GitHub will be the master storage location for all project files, source code, documentation, build plans, logs, and recovery instructions.

**Why:** Prevents loss of work if chat context is lost. Enables version history, recovery, and professional project governance.

## DEC-002 — Build as Portfolio Edition v1.0

**Decision:** The first public release will be named Portfolio Edition v1.0.

**Why:** This is clearer and more credible than continuing internal version labels such as V9.5.

## DEC-003 — Packaging First, Raw Materials Later

**Decision:** v1.0 will implement the Packaging Procurement Engine first. v1.1 will add a Raw Material Procurement Engine.

**Why:** Packaging is the strongest domain-fit for the first build. Raw materials should be added through the same category-engine architecture after the platform foundation is stable.

## DEC-004 — Transparent Rule-Guided AI-Ready Architecture

**Decision:** Award logic will remain deterministic, visible, and auditable. AI will support extraction, drafting, explanation, and summarization, not autonomous award decisions.

**Why:** Procurement decisions require governance, explainability, accountability, and human control.

## DEC-005 — Modular Architecture

**Decision:** Build as a modular software product, not a single-use Streamlit script.

**Why:** Modular design improves maintainability, extensibility, interview credibility, and future conversion to other interfaces.
