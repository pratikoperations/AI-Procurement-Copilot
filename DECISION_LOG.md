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

## DEC-006 — Defer Time-Aware Procurement Analytics Until After v1.0

**Decision:** Date-range selection, historical trend analysis, period-over-period comparison, quarter-over-quarter comparison, year-over-year comparison, and rolling-period analytics will be implemented only after Portfolio Edition v1.0 is released. The recommended target is Version 1.1 — Time-Aware Procurement Analytics.

**Why:** Time-aware analytics has high procurement value but requires historical data, governing date fields, schema changes, period-comparison rules, export metadata, and safeguards against false precision. Adding it during the release-candidate phase would break the feature freeze and reopen calculation, UX, export, and regression risk.

**Design constraints:**

- Every module must declare its governing date field.
- Missing dates must never be silently assigned to the current period.
- Incomplete periods must be labelled.
- Comparisons must be suppressed when prior-period data is not comparable.
- Screens and exports must disclose the reporting period and data coverage.
- Snapshot data and historical data must be clearly distinguished.

**Reference:** `docs/FUTURE_TIME_AWARE_ANALYTICS.md`
