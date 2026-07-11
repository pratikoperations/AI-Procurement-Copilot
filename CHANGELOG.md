# Changelog

All meaningful project changes will be recorded here.

## Build 0.8 — Portfolio Edition v1.0 Release Candidate

### Added

- Export regression tests covering CSV, TXT, JSON, and Excel outputs.
- Automated Streamlit health smoke test.
- GitHub Actions workflow extended to run regression, export, compile, and Streamlit smoke checks.
- Portfolio resume and LinkedIn assets.
- Seven-minute interview demo script.
- Screenshot capture guide and naming standard.
- Release-candidate labels in `app.py` and `modules/config.py`.
- Build 0.8 QA report and updated project status.

### QA Notes

- Core CI was green before Build 0.8.
- Build 0.8 adds broader automated coverage.
- Latest Build 0.8 workflow result, manual visual review, sample upload, and download-button verification remain pending.

## Build 0.7 — Defect Remediation, Visual Polish, Downloadable Outputs, and Release-Candidate Preparation

### Added

- `modules/exports.py` for CSV, TXT, JSON, and Excel decision-package exports.
- Download center for supplier scores, allocation, executive memo, supplier email, Excel workbook, and JSON package.
- Six-step interview-demo workflow.
- Release-candidate application messaging and status.
- `docs/RELEASE_CANDIDATE_CHECKLIST.md`.
- Updated project status and version manifest.

### QA Notes

- Static integration review completed.
- Export logic added and connected.
- GitHub Actions import-path defect remediated.
- Latest Build 0.7 workflow runs passed.

## Build 0.6 — UX Refinement, Testing, Documentation, and Portfolio Polish

### Added

- Structured RFQ validation and scored-output validation.
- Tabbed Streamlit workflow for decision summary, analysis, strategy, executive outputs, and interview guide.
- Error handling for unreadable RFQ files and scoring failures.
- Regression tests for demo data, should-cost logic, stress response, score ordering, and annual TCO consistency.
- GitHub Actions quality-check workflow.
- `docs/USER_GUIDE.md`.
- Updated README with current capabilities, run instructions, inputs, and outputs.
- Updated build labels and project status.

### QA Notes

- Static integration review completed.
- Automated tests and compile checks configured in GitHub Actions.

## Build 0.5 — Executive Communication Layer

### Added

- Formal `QUALITY_ASSURANCE_PROTOCOL.md`.
- Executive sourcing memo generator.
- Supplier clarification email generator.
- AI-style explainability panel generator.
- Interview talking points generator.
- Streamlit UI integration for all Build 0.5 outputs.
- Updated build labels in `app.py` and `modules/config.py`.
- Project status updated for Build 0.5.

### QA Notes

- Static integration review completed.
- Documentation updated.

## Build 0.4 — Decision Intelligence, Allocation, Scenario Simulation, and Negotiation

### Added

- Base build plan reference summary in `docs/BASE_BUILD_PLAN_REFERENCE.md`.
- Lowest-price vs best-value decision logic.
- Recommendation confidence calculation.
- Executive value breakdown.
- Constraint-style supplier allocation engine.
- Scenario stress-testing engine.
- Negotiation simulator.
- Negotiation playbook generator.
- Allocation controls in sidebar.
- Dashboard sections for executive value, allocation, scenario testing, and negotiation.
- App integration for Build 0.4 decision intelligence modules.

### Notes

Build 0.4 brings the app closer to the uploaded V9.5 base plan while keeping the code modular and recoverable.

## Build 0.3 — Packaging Procurement Engines

### Added

- Working packaging should-cost engine with auditable component assumptions.
- Should-cost dataframe with unit and annual USD/INR impact.
- Structured supplier risk engine covering payment, incoterms, lead time, MOQ, service, and quality.
- Advanced TCO engine covering scenario price, freight exposure, inventory cost, working capital, risk penalty, and lead-time buffer.
- ESG scoring engine for recyclability, certification, carbon score, EPR readiness, and PCR content.
- Supplier performance scoring engine for OTIF, quality PPM, audit score, complaint rate, and capacity buffer.
- Weighted supplier scoring engine.
- Dashboard sections for executive summary, supplier snapshot, should-cost, and TCO breakdown.
- Enriched synthetic and sample RFQ data.

### Notes

Build 0.3 turns the app from a skeleton into a working procurement analytics engine.

## Build 0.2 — Streamlit Framework and Modular Application Skeleton

### Added

- Modular Streamlit app framework.
- Sidebar controls for data source, category engine, currency, volume, and scenario assumptions.
- Dashboard rendering module.
- Synthetic packaging RFQ starter data.
- RFQ upload loader and column validation placeholder.
- Utility module.
- Placeholder modules for should-cost, TCO, risk, ESG, performance, allocation, negotiation, recommendation, and charts.
- Sample packaging RFQ CSV file.

### Notes

Build 0.2 creates the application skeleton.

## Build 0.1 — Repository Foundation

### Added

- Created project README.
- Added project status tracking.
- Added foundation documentation structure.
- Established GitHub as canonical source of truth.
- Locked version strategy: v1.0 Packaging, v1.1 Raw Materials, v2.0 Multi-category platform.

### Notes

Build 0.1 focused on repository safety, documentation, recovery, and governance.
