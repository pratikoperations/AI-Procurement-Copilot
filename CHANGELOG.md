# Changelog

All meaningful project changes are recorded here.

## Build 1.0 RC1.2.2 — Export Score Consistency and Scenario Integrity Hotfix

### Fixed

- Differentiated RFQ Performance and ESG scores from governed Supplier Intelligence scores.
- Added governed Supplier 360 Performance, Financial, ESG, Innovation, and Supplier 360 fields to readable score reports.
- Corrected Freight +50% scenario behavior for DDP and other delivered-price suppliers.
- Preserved zero incremental freight in base-case DDP pricing while stressing embedded freight only during explicit freight shocks.
- Replaced Risk Score with Risk Resilience Score in readable scenario exports.
- Replaced Advanced TCO Unit USD with category-aware Risk-Adjusted TCO per unit labels.
- Added Packaging and Raw Material freight-scenario regression coverage.

### Validation Notes

- No new business feature was introduced.
- No score weighting or recommendation philosophy changed.
- Feature freeze remains active.
- GitHub Actions, Streamlit smoke testing, and manual export retest remain pending.

## Build 1.0 RC1.2.1 — Supplier 360 Display Formatting Hotfix

### Fixed

- Corrected Approved Categories and Commodity Coverage rendering in Supplier 360 profiles.
- Strings are now displayed directly instead of being split character by character.
- Lists, tuples, and sets are joined as readable comma-separated values.
- Applied the same safe display formatting to reusable key-value profile components.
- Added regression coverage for scalar and collection display behavior.

## Build 1.0 RC1.2 — Export Integrity and Category-Aware Communication Hotfix

### Added

- Currency and unit governance with original and normalized quotation fields.
- Category-aware supplier communication for Packaging and Raw Material procurement.
- Eligibility-aware executive memo and supplier email wording.
- Governed recommendation roles using displayed scores and evidence sufficiency.
- Classification precedence between Exit Candidate and Development Candidate.
- Business-readable supplier score and comparison reports.
- Export consistency, communication, currency, recommendation, and precedence tests.
- Download content audit and governance documentation.

### Changed

- Corrected Raw Material synthetic demo currency and unit metadata.
- Standardized PET Resin to kg.
- Renamed visible risk terminology to Risk Resilience Score.
- Separated business-readable downloads from machine-readable audit data.
- Prevented unsupported Most Innovative, Most Sustainable, Best Strategic Partner, and Best Long-Term Supplier claims.
- Added no-qualified-supplier outcomes when evidence is insufficient.

## Build 1.0 RC1.1 — Final Executive Polish

- Replaced technical chart legends with executive labels.
- Standardized score and TCO axis titles.
- Replaced generic deterministic-comparison wording with recommendation-specific business explanations.
- Corrected Raw Material should-cost heading.

## Build 0.9.6.1 — Executive-Readable Supplier Intelligence UX Hotfix

- Replaced raw structured Supplier Intelligence output with executive-readable cards, charts, matrices, evidence lists and action plans.
- Added evidence-governance caps for Financial, ESG and Innovation outputs.
- CI and live mobile validation passed.

## Build 0.9.6 — Independent Validation and Real-World Stress Testing

- Added data-confidence, recommendation eligibility, business-rule validation, adversarial tests, external-file validation, defect governance and release controls.
- Quality Checks #150–#208 confirmed green.

## Earlier Builds

Completed repository foundation, packaging and raw-material engines, executive outputs, CI, deployment stabilization, multi-category architecture, Intelligent RFQ, Procurement Intelligence, and Supplier Intelligence.
