# Changelog

All meaningful project changes are recorded here.

## Unreleased — Cross-LLM Portability Foundation

### Added

- Portability risk assessment.
- AI and human developer handoff guide.
- Project architecture and protected business-rule documentation.
- Governed data dictionary and missing-data rules.
- Reproducible setup, deployment, and troubleshooting guides.
- Contribution workflow for AI-generated changes.
- Environment-variable template with no real credentials.
- Test-structure and regression-coverage guidance.

### Changed

- Documentation now makes GitHub, rather than AI conversation history, the explicit source of truth.
- No application logic, formula, threshold, dependency, or runtime behaviour changed.

## Version 1.0.0 — Stable Portfolio Edition

### Released

- First stable release of AI Procurement Copilot.
- Packaging Procurement and Raw Material Procurement engines.
- Category-aware should-cost, TCO, risk, scoring, allocation, negotiation, and scenario analysis.
- Procurement Intelligence and Supplier Intelligence.
- Supplier 360 with performance, financial, ESG, innovation, and SRM indicators.
- Data-confidence, recommendation-eligibility, and business-rule governance.
- Category-aware executive memo, supplier email, and supplier narrative.
- Business-readable CSV, TXT, and Excel reports.
- Separate machine-readable decision and Supplier 360 audit exports.
- Mobile-ready Streamlit interface.
- Regression, adversarial, external-file, UI, scenario, export, and governance tests.

### Release Validation

- GitHub Actions passed.
- Streamlit smoke test passed.
- Packaging and PET Resin live workflows passed.
- Multi-Scenario Stress Test passed after RC1.2.3 schema alignment.
- Readable reports and Excel workbook were directly inspected.
- No open Major or Critical defect remained at approval.

### Known Limitations

- Financial, ESG, and innovation outputs remain evidence-dependent and may be capped when data is incomplete.
- Human procurement approval and due diligence remain mandatory.
- Time-aware procurement analytics is deferred to Version 1.1.

## Build 1.0 RC1.2.3 — Scenario Engine Column Alignment Critical Hotfix

- Aligned the dashboard renderer with governed scenario headings.
- Removed the live `Annual TCO USD` KeyError.
- Preserved compatibility with governed and legacy scenario schemas.
- Added Packaging and Raw Material scenario-schema tests.

## Build 1.0 RC1.2.2 — Export Score Consistency and Scenario Integrity Hotfix

- Differentiated RFQ Performance and ESG scores from governed Supplier Intelligence scores.
- Added governed Supplier 360 Performance, Financial, ESG, Innovation, and Supplier 360 fields to readable score reports.
- Corrected Freight +50% scenario behavior for DDP and other delivered-price suppliers.
- Replaced Risk Score with Risk Resilience Score in readable scenario exports.
- Added category-aware Risk-Adjusted TCO labels.

## Build 1.0 RC1.2.1 — Supplier 360 Display Formatting Hotfix

- Corrected Approved Categories and Commodity Coverage rendering.
- Added safe scalar and collection display formatting.

## Build 1.0 RC1.2 — Export Integrity and Category-Aware Communication Hotfix

- Added explicit currency and unit governance.
- Added category-aware and eligibility-aware communications.
- Governed recommendation roles using evidence sufficiency.
- Separated readable exports from machine-readable audit data.

## Build 1.0 RC1.1 — Final Executive Polish

- Replaced technical chart labels and recommendation wording.
- Standardized category headings and executive terminology.

## Build 0.9.6.1 — Executive-Readable Supplier Intelligence UX Hotfix

- Replaced raw structured output with executive-readable Supplier Intelligence.
- Added Financial, ESG, and Innovation evidence-governance safeguards.

## Build 0.9.6 — Independent Validation and Real-World Stress Testing

- Added data-confidence, eligibility, business-rule validation, adversarial tests, external-file validation and release governance.

## Earlier Builds

Completed repository foundation, category engines, executive outputs, Procurement Intelligence, Supplier Intelligence, CI, deployment, and validation governance.
